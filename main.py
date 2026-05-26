"""
Badger Support Agent
Slack bot that categorizes, assigns, and tracks issues for Unlock Investment Operations
"""

import os
import json
import hmac
import hashlib
import logging
import time
import re
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager

import uvicorn
import anthropic
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from rank_bm25 import BM25Okapi

# DOMAIN_EXPANSIONS for Badger Support Agent
# Maps Investment Operations / servicing ops terminology to code identifiers
# Used by the BM25 KB search to translate operator language into searchable terms
# Add new terms as the team introduces new concepts or workflows

DOMAIN_EXPANSIONS = {

    # ── CORE IDENTIFIERS ────────────────────────────────────────────────────
    "asset":                        "asset_id BadgerLib.Assets GetSingleAttribute",
    "asset id":                     "asset_id vAssetsEx",
    "file number":                  "file_num file_number GetFileNumByAssetId",
    "file num":                     "file_num closing",
    "deal":                         "asset_id investment_payment HEA",
    "hea":                          "asset_id investment_payment exchange_rate oface",
    "home equity agreement":        "asset_id oface investment_payment",

    # ── FINANCIAL / INVESTMENT AMOUNTS ──────────────────────────────────────
    "original face":                "oface",
    "original face value":          "oface",
    "investment amount":            "oface investment_payment",
    "investment payment":           "investment_payment oface Fundings_New",
    "net wire":                     "net_wire_amt",
    "net wire amount":              "net_wire_amt investment_payment",
    "origination fee":              "origination_fee",
    "appraisal fee":                "appraisal_fee GetMTIDbyAssetId_AppraisalFee",
    "gain on sale":                 "gain_on_sale CalculateGainOnSale purchase_proceeds",
    "purchase proceeds":            "purchase_proceeds CreatePurchaseProceedsLedgerAccountAsync",
    "gos":                          "gain_on_sale purchase_proceeds",
    "haircut":                      "haircut Fundings_New investment_payment",
    "unlock haircut":               "haircut UPS oface investment_payment",
    "tcb advance":                  "DrawFlow CreateInvestmentPaymentLedgerTransactionAsync",
    "draw":                         "DrawFlow MTDrawGlobals CreateInvestmentPaymentLedgerTransactionAsync",
    "draw request":                 "UF2 DrawFlow borrowing_base TCB",
    "draw amount":                  "oface investment_payment DrawFlow",

    # ── ACCOUNTS / ENTITIES ─────────────────────────────────────────────────
    "ups":                          "UPS account balance_sheet JPM",
    "uf2":                          "UF2 funding_account TCB x3836",
    "uf2 funding account":          "UF2 x3836 TCB DrawFlow",
    "uf2 collections":              "UF2 x3844 settlement_wire incoming",
    "collections account":          "x3844 UF2 settlement_wire",
    "tcb":                          "TCB Texas_Capital_Bank warehouse_line DrawFlow",
    "texas capital bank":           "TCB warehouse_line DrawFlow securelogin.texascapitalbank.com",
    "wsfs":                         "WSFS custodygroup@wsfsbank.com certification shipment",
    "cet":                          "ClearEdge CETWireReportTemplate ClearEdgeLoads",
    "clearEdge":                    "CET ClearEdge ClearEdgeWireReports ClearEdgeLoads",
    "first american":               "FA FirstAmerican title_company",
    "fa":                           "FirstAmerican FA title_company",
    "suntera":                      "Suntera ICS investment_closing_statement",
    "saluda":                       "Saluda SGALT SGLT counterparty vTradesEx",
    "sgalt":                        "SGALT counterparty Saluda trade_id",
    "d2":                           "D2 UNSO counterparty vTradesEx",
    "libremax":                     "LibreMax LEX1 LEX2 assignment borrowing_base",
    "lex1":                         "LEX1 LibreMax vTradesEx account",
    "lex2":                         "LEX2 LibreMax vTradesEx account",
    "bsi":                          "BSI backup_servicer bsi_investor_code Accounts",
    "maxwell":                      "Maxwell diligence Maxwell_Diligence_Asset_Map",
    "sgof":                         "SGOF MSR_purchaser excess_servicing",
    "modern treasury":              "ModernTreasury ModernTreasuryUtils InsertModernTreasuryMap",

    # ── SETTLEMENT ──────────────────────────────────────────────────────────
    "settlement":                   "settlement_type settlement_reason SettlementFlow",
    "settlement wire":              "GetIncomingSettlementWires vIncomingSettlementWires x3844",
    "incoming wire":                "GetIncomingSettlementWires vIncomingSettlementWires",
    "settlement calculator":        "SettlementCalculator settlement_type net_settlement_payment",
    "settlement fee":               "settlement_fee 500 waived Unlock_Refinance",
    "lien release fee":             "lien_release_fee 75",
    "exercise value":               "exercise_value investor settlement_proceeds",
    "settlement quick publisher":   "SettlementQuickPublish JPM_Formatted xlsm",
    "quick publisher":              "SettlementQuickPublish settlement_type",
    "cancel settlement":            "ResetSettlement dbo.ResetSettlement",
    "delete settlement":            "ResetSettlement month_of_tab tracker",
    "underpayment":                 "underpayment GetTCBBankTrans tcbinv_id Christine",
    "overpayment":                  "overpayment refund JPM_UAM customer",
    "reo":                          "REO reo_settlement_date reo_net_proceeds reo_home_sale_price",
    "reo sale":                     "REO auction x8972 net_proceeds",
    "foreclosure":                  "REO auction FCL lien_alert foreclosure_type",
    "right of rescission":          "uwissue_id 6 ProcessAssetFailedToClose rescission",
    "failed to close":              "ProcessAssetFailedToClose uwissue_id fundingstatus_id",
    "cancellation":                 "ProcessAssetFailedToClose fundingstatus_id 4 Fundings_New",
    "banktrans id":                 "tcbinv_id BANKTRANS_ID GetTCBBankTrans CashTransactions",
    "bank trans":                   "tcbinv_id tcb_banktrans_id GetTCBBankTrans",

    # ── FUNDING / PIPELINE ──────────────────────────────────────────────────
    "funding":                      "Fundings_New investment_payment DrawFlow funding_date",
    "daily funding":                "Fundings_New BulkFunding value_date investment_payment",
    "bulk funding":                 "BulkFunding Fundings_New escrow_button haircut_button",
    "escrow button":                "BulkFunding Fundings_New pending_escrow_disbursement",
    "haircut button":               "haircut Fundings_New Trades journal_entries",
    "badger money button":          "Fundings_New BulkFunding unfunded breakdown_tabs",
    "max button":                   "MAX substage pending_recording Fundings_New Funded ICS",
    "pending escrow disbursement":  "Fundings_New BulkFunding substage",
    "pending recording":            "substage MAX Fundings_New Funded",
    "value date":                   "funding_date value_date BulkFunding",
    "effective date":               "effective_date funding_date vAssetsEx",
    "pipeline":                     "pipeline_label customer_pipeline_label_max GetPipelineLabel",
    "pipeline label":               "pipeline_label Fundings_New account vAssetsEx",
    "dbsync":                       "run_max_new_dbsync.bat DBSync MAX",
    "dbloader":                     "DBLoader bat cet_manifest lienalert WSFS",

    # ── TRADES ──────────────────────────────────────────────────────────────
    "trade":                        "Trades vTradesEx trade_id trade_date settle_date",
    "paper a trade":                "Trades vTradesEx Forward_Sale_Data_Schedule tape",
    "tape":                         "New_Tape_Format_v8.sql vTradesEx vAssetsEx cutoff",
    "position tape":                "New_Tape_Format_v8.sql cutoff include_zero_positions",
    "strats":                       "Strats_Template.xlsb Single_Guitar bucket_investment_payment",
    "strats report":                "Strats_Template.xlsb PDF Single_Guitar",
    "available collateral":         "Certified Disbursed WSFS CET trades_setup_template",
    "certified":                    "WSFS Schedule_I certification custody",
    "disbursed":                    "CET funds_disbursed badger_growls ClearEdgeWireReports",
    "trade date":                   "trade_date settle_date Trades vTradesEx",
    "settle date":                  "settle_date WSFS custody_transfer Trades",
    "exchange rate":                "exchange_rate cost_limit vAssetsEx trade_price",
    "base exchange":                "exchange_rate base_price round_down",
    "counterparty":                 "counterparty SGALT D2 UF2 JOURNAL vTradesEx",
    "buyback":                      "is_unlock_buyback_acct buy_sell B Trades",
    "buy sell":                     "buy_sell Trades B S vTradesEx",
    "securitization":               "UNLOK 2022-1 2023-1 2024-1 securitization_account",
    "diligence":                    "Maxwell Maxwell_Diligence_Asset_Map Diligence_Name 20%",
    "maxwell diligence":            "Maxwell_Diligence_Asset_Map himaxwell diligence_war_room",

    # ── CUSTODY / COLLATERAL ────────────────────────────────────────────────
    "custody":                      "WSFS ClearEdge shipment electronic_package",
    "shipment":                     "Badger_shipment WSFS staging electronic_custody",
    "collateral":                   "WSFS custody certified Available_Collateral",
    "collateral release":           "WSFS ReportRunner WSFSCustodyToday.bat settle_date",
    "assignment":                   "Assignment_of_Security Generate_Assignment LEX1 LEX2",
    "assignment of security":       "sp_Generate_Assignment_of_Security LEX1 LEX2",
    "manifest":                     "CET_manifest cet_manifest.bat shipments ClearEdge",
    "cet manifest":                 "cet_manifest.bat ClearEdge shipments WSFS",
    "wsfs certification":           "WSFS Schedule_I List_of_Loans certification",
    "schedule i":                   "WSFS_List_Of_Loans DBLoader certification",
    "schedule ii":                  "WSFS exceptions post_closing",
    "bsi tape":                     "Backup_Servicing_Tape.sql bsi_investor_code SSMS",
    "backup servicer":              "BSI bsi_investor_code Accounts quarterly",

    # ── REPORTING ───────────────────────────────────────────────────────────
    "remittance":                   "RemittanceFeesFlow remittance_period AMA waterfall",
    "remittance report":            "AMA waterfall AM_fee disposition_fee incentive_fee",
    "am fee":                       "asset_management_fee AMA remittance",
    "disposition fee":              "disposition_fee remittance AMA settlement",
    "incentive fee":                "incentive_fee AMA remittance",
    "borrowing base":               "LibreMax EWB borrowing_base LEX1 LEX2",
    "libremax borrowing base":      "New_Tape_Format_v8-LibreMax_Borrowing_Base.sql LEX1 LEX2",
    "equity balance":               "LibreMax State_Street equity_position PDF DocuSign",
    "msr":                          "MSRSaleFlow msr_trade_id msr_asset_ledger_account_id",
    "mortgage servicing rights":    "MSRSaleFlow msr_revenue_account_id GetMTIDbyAssetId_MSRAsset",
    "npv":                          "NPV XIRRCalculator MSR CashflowEngine",
    "xirr":                         "XIRRCalculator NPV Analytics",
    "cashflow":                     "CashflowEngine CashflowSingle CashflowInputs",
    "pricing":                      "PricingEngine PricingInputs PricingOutput",
    "hpi":                          "YoYAppreciation ZHVI Zillow HPI trg_HPI",
    "home price index":             "ZHVI Zillow HPI YoYAppreciation",
    "zillow":                       "ZHVI Zillow UpdateZillowBulk HPI",
    "zhvi":                         "Zillow ZHVI UpdateZillowBulk hpitype_id",
    "cpr":                          "CPR prepayment_rate Prepay_Calendar",
    "cdr":                          "CDR default_rate Performance_Report ByCalendar",
    "wavg":                         "weighted_average WAVG credit_score CLTV ACL",
    "wtd average":                  "weighted_average WAVG Strats",
    "cltv":                         "CLTV combined_loan_to_value vAssetsEx",
    "dlq":                          "delinquency DLQSummaryByAccount PostCreditLoad",
    "delinquency":                  "DLQSummaryByAccount CRQueue CreditScores",
    "monthly reporting":            "Strats investor_reporting month_end tape",
    "month end":                    "cutoff New_Tape_Format_v8 month_end_tape",
    "month end tape":               "New_Tape_Format_v8 cutoff TOAD vAssetsEx",
    "origination tape":             "Unlock_Historical_Origination_Tape month_end position",
    "d2 tape":                      "D2 monthly_origination_tape glinton@d2-am.com",
    "d2 pipeline":                  "D2 weekly_pipeline_report Omni Funnel_Pipeline",
    "saluda strats":                "Saluda SGALT SGLT Strats_Template Single_Guitar",
    "investor reporting":           "strats tapes investor_reporting Slack #investor_reporting",

    # ── CREDIT ──────────────────────────────────────────────────────────────
    "credit pull":                  "CRS MeridianLink CreditTradeLinesSimple CreditScores",
    "credit score":                 "CreditScores ProcessTradeLinesSimple vantage FICO",
    "vantage":                      "Vantage TransUnion CreditScores monthly",
    "fico":                         "FICO TransUnion CreditScores quarterly",
    "credit report":                "CRS CRQueue ProcessCreditReportNew CreditLoads",
    "tradeline":                    "CreditTradeLinesSimple CreditTradeLinesRaw mortgage_tradeline",
    "mortgage tradeline":           "CreditTradeLinesSimple Debt craccount_id",
    "tradeline mapping":            "TradeLineMapping.sql craccount_id Debt payment_threshold",
    "automap":                      "TradeLineMapping.sql update_bit CRQueue craccount_id",
    "credit mapping":               "TradeLineMapping.sql craccount_id #credit_mapping_committee",

    # ── LIEN ALERTS ─────────────────────────────────────────────────────────
    "lien alert":                   "LienAlert LALoads Black_Knight lienalert.bat",
    "lien alerts":                  "LienAlert sp_post_lien_alerts_proc surveillance",
    "surveillance":                 "LienAlert surveillance_alerts Nick_Carnot Brandan_Carlson",
    "black knight":                 "BlackKnight LienAlert goanywherecltnr.bkiconnect.com",
    "refresh file":                 "Active_HEI_Portfolio.refresh LienAlertsRefreshGenerateAndUpload.py",

    # ── MODERN TREASURY / LEDGER ─────────────────────────────────────────────
    "ledger":                       "CreateLedgerAssetCategoryAsync CreateLedgerSubCategoryAsync ModernTreasury",
    "ledger account":               "CreateInvestmentPaymentLedgerAccountAsync ledger_account",
    "backfill":                     "Backfill RunAsync ModernTreasuryUtils InsertModernTreasuryMap",
    "contra account":               "backfill_contra_account_id investor_contra_memo_account_id",
    "memo account":                 "investor_memo_account_id GetMemoAccountsByAccountID",

    # ── SYSTEM / ADMIN ───────────────────────────────────────────────────────
    "import asset":                 "sp_MAX_Badger_Import_All UAM_flaire API_XXXXX",
    "second deal":                  "MapSecondDealApplicant AssetApplicantMap second_deal",
    "pre check":                    "sp_MAX_Badger_Import_All PreCheck closing_table",
    "applicant":                    "AssetApplicantMap applicant_id applicanttype_id",
    "encrypted column":             "CEK_Auto1 APPLICATION_SECRET Azure certificate",
    "ssn":                          "Applicants CEK_Auto1 encrypted SSMS Azure_AD",
    "key expiry":                   "APPLICATION_SECRET Azure certificate_secret expiry",
    "zensync":                      "Zensync Zendesk ZenSync_Runs Load_Users Load_Tickets",
    "zendesk":                      "Zensync Zendesk ZenSync_Runs defaults_cache",
    "margin call":                  "TCB margin_call UPS x0292 UF2 x3844 30_days",
    "report runner":                "ReportRunner.exe bat ReportRunner sql_file",
    "omni":                         "Omni unlocktechnologies.omniapp.co dashboard",
    "sigma":                        "Sigma trades_report historic_trades",
    "a drive":                      "A:\\ network_drive applications DBLoader DBSync",
    "dbloader":                     "DBLoader bat WSFS lienalert cet_manifest",
    "conveyance":                   "Conveyance_Offer_Tape NJ PA AZ MN regulatory",
    "docusign":                     "DocuSign draw_confirmation bill_of_sale signing",
    "hellosign":                    "HelloWorks signing document",
    "sharepoint":                   "SharePoint document_storage integrations",

    # ── VALUATIONS / AVM ─────────────────────────────────────────────────────
    "avm":                          "AVMRunner Valuations CoreLogic GetAVMValueInternal valuationtype_id",
    "automated valuation":          "AVMRunner Valuations CoreLogic apn estimatedValue",
    "valuation":                    "Valuations AVMRunner valuationtype_id highValue lowValue",
    "corelogic":                    "CoreLogicLib AVMRunner client_id GetPropertyID",
    "apn":                          "apn address_1 zip Valuations GetNeededValuations",
    "property value":               "AVMRunner Valuations estimatedValue highValue lowValue",
    "home value":                   "Valuations AVMRunner starting_home_value current_home_value",

    # ── RUNNERS / LOADERS ────────────────────────────────────────────────────
    "avm runner":                   "AVMRunner Valuations CoreLogic scheduled_runner",
    "alert runner":                 "AlertRunner surveillance LienAlert scheduled",
    "credit runner":                "CreditRunner LoadSingleCRSRequest ProcessCreditPull CRSLib",
    "tax pull":                     "CRSLib TaxPullRequest TaxOrderRequest CRS",
    "crs tax":                      "CRSLib TaxPullRequest TaxOrderRequest credit_reporting",
    "bigdough":                     "BigDoughLoad BigDoughLib finance_ops",
    "bank lib":                     "BankLib Accounts Transactions InsertTransaction",

    # ── SLACK CHANNELS (CODE IDENTIFIERS) ────────────────────────────────────
    "uf2 activity":                 "uf2_activity RECIPIENT SlackLib UF2",
    "allocations strategy":         "allocations_strategy RECIPIENT SlackLib",
    "deal review":                  "deal_review RECIPIENT SlackLib",
    "servicing channel":            "servicing RECIPIENT SlackLib",
    "slack recipient":              "TAGGED_RECIPIENT RECIPIENT SlackLib hooks slack_tag vUsers",
    "team uam":                     "team_uam RECIPIENT SlackLib PostCreditLoad",

    # ── TEAM MEMBERS (TAGGED RECIPIENTS) ─────────────────────────────────────
    "jagat":                        "Jagat_Shah TAGGED_RECIPIENT jagat.shah@unlock.com",
    "ryan thrift":                  "Ryan_Thrift TAGGED_RECIPIENT ryan.thrift@unlock.com",
    "zach winslow":                 "Zach_Winslow TAGGED_RECIPIENT zach.winslow@unlock.com",
    "john park":                    "John_Park TAGGED_RECIPIENT john.park@unlock.com",
    "justin burke":                 "Justin_Burke TAGGED_RECIPIENT credit_mapping tradeline",
    "nick carnot":                  "Nick_Carnot TAGGED_RECIPIENT lien_alerts surveillance",
    "brandan carlson":              "Brandan_Carlson TAGGED_RECIPIENT lien_alerts surveillance",
    "brian rubin":                  "Brian_Rubin TAGGED_RECIPIENT monthly_reporting strats",
    "kevin nerney":                 "Kevin_Nerney TAGGED_RECIPIENT LibreMax equity_balances",
    "jim muhich":                   "Jim_Muhich TAGGED_RECIPIENT jim@unlock.com",
    "paul fanning":                 "Paul_Fanning TAGGED_RECIPIENT paul.fanning@unlock.com",
    "rick panebianco":              "Rick_Panebianco TAGGED_RECIPIENT rick.panebianco@unlock.com",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


# ── CONFIGURATION ──────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY    = os.environ.get("ANTHROPIC_API_KEY", "")
SLACK_BOT_TOKEN      = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")

MODEL             = "claude-sonnet-4-6"
KB_DIR            = Path(__file__).parent / "kb"
DB_PATH           = Path(__file__).parent / "tickets.db"
CHUNK_SIZE        = 100
CHUNK_OVERLAP     = 20
TOP_K             = 20
MAX_CONTEXT_CHARS = 60_000

# ── CATEGORY / ASSIGNMENT CONFIG ───────────────────────────────────────────────

CATEGORIES = {
    "Badger":               {"assignee": "Jagat Shah",  "email": "jagat.shah@unlock.com"},
    "Excel Toolkits":       {"assignee": "Jagat Shah",  "email": "jagat.shah@unlock.com"},
    "Deal Data Quality":    {"assignee": "Brian Rubin", "email": "brian.rubin@unlock.com"},
    "Data Ad Hoc Request":  {"assignee": "Jagat Shah",  "email": "jagat.shah@unlock.com"},
}

AD_HOC_TEAMS = [
    "Investor", "Legal", "Servicing",
    "Capital Markets", "Accounting", "Portfolio Management",
]

TICKET_STATUSES = ["New", "Assigned", "In Progress", "Resolved"]

ANCHOR_KEYWORDS = {
    "logic_team_ownership.txt":    ["Jagat", "Brian"],
    "logic_system_operations.txt": ["KEY SLACK CHANNELS"],
}


# ── DATABASE ───────────────────────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at     TEXT NOT NULL,
            submitted_by   TEXT NOT NULL,
            description    TEXT NOT NULL,
            category       TEXT NOT NULL,
            sub_category   TEXT,
            assignee       TEXT NOT NULL,
            assignee_email TEXT NOT NULL,
            status         TEXT NOT NULL DEFAULT 'New',
            slack_channel  TEXT,
            thread_ts      TEXT
        )
    """)
    conn.commit()
    conn.close()


def create_ticket(submitted_by, description, category, sub_category, slack_channel, thread_ts):
    cat = CATEGORIES[category]
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.execute("""
        INSERT INTO tickets (created_at, submitted_by, description, category,
                             sub_category, assignee, assignee_email, status,
                             slack_channel, thread_ts)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'New', ?, ?)
    """, (datetime.utcnow().isoformat(), submitted_by, description, category,
          sub_category, cat["assignee"], cat["email"], slack_channel, thread_ts))
    ticket_id = cur.lastrowid
    conn.commit()
    conn.close()
    return ticket_id


def get_tickets():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_ticket_status(ticket_id, status):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE tickets SET status=? WHERE id=?", (status, ticket_id))
    conn.commit()
    conn.close()


# ── KB / BM25 ──────────────────────────────────────────────────────────────────

def load_kb_chunks():
    corpus, meta = [], []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for fpath in sorted(KB_DIR.rglob("*")):
        if not fpath.is_file():
            continue
        try:
            text = fpath.read_text(errors="replace")
        except Exception:
            continue
        lines = text.splitlines()
        for i in range(0, max(1, len(lines) - CHUNK_OVERLAP), step):
            chunk = "\n".join(lines[i: i + CHUNK_SIZE])
            corpus.append(chunk.lower().split())
            meta.append({"file": fpath.name, "start": i, "text": chunk})
    log.info(f"Loaded {len(corpus)} KB chunks")
    return corpus, meta


def build_anchor_chunks(meta):
    seen, anchors = set(), []
    for m in meta:
        for kw in ANCHOR_KEYWORDS.get(m["file"], []):
            if kw.lower() in m["text"].lower():
                h = hashlib.md5(m["text"].encode()).hexdigest()
                if h not in seen:
                    seen.add(h)
                    anchors.append(m["text"])
                break
    return anchors


# ── GLOBAL STATE ───────────────────────────────────────────────────────────────

_bm25:         Optional[BM25Okapi] = None
_meta:         list                = []
_anchors:      list                = []
_seen_events:  dict                = {}
_pending_adhoc: dict               = {}  # (channel, user) → {description, thread_ts}

slack_client  = WebClient(token=SLACK_BOT_TOKEN)
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _bm25, _meta, _anchors
    init_db()
    corpus, _meta = load_kb_chunks()
    _bm25 = BM25Okapi(corpus)
    _anchors = build_anchor_chunks(_meta)
    log.info(f"Ready. {len(_meta)} chunks, {len(_anchors)} anchors.")
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── CLASSIFICATION ─────────────────────────────────────────────────────────────

CLASSIFY_PROMPT = """\
You are a ticket classifier for Unlock Technologies Badger servicing system.
Classify the issue into exactly one category:
  - Badger           (system errors, application issues, asset imports, Badger app bugs)
  - Excel Toolkits   (macro errors, #NAME? errors, PopulateAsset failures, calculator issues)
  - Deal Data Quality (missing or incorrect deal/asset data, tradeline issues, credit data)
  - Data Ad Hoc Request (one-off data pulls, report requests, data extracts)

Respond with ONLY valid JSON. No markdown. No explanation.
Example: {"category": "Badger"}
"""

def classify_issue(description):
    try:
        r = claude_client.messages.create(
            model=MODEL, max_tokens=50,
            system=CLASSIFY_PROMPT,
            messages=[{"role": "user", "content": description}],
        )
        data = json.loads(r.content[0].text.strip())
        cat  = data.get("category", "")
        if cat in CATEGORIES:
            return cat
    except Exception as e:
        log.error(f"Classification error: {e}")
    return "Badger"


# ── SLACK HELPERS ──────────────────────────────────────────────────────────────

def verify_slack_signature(body, timestamp, signature):
    base     = f"v0:{timestamp}:{body.decode('utf-8')}"
    computed = "v0=" + hmac.new(SLACK_SIGNING_SECRET.encode(), base.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(computed, signature)


def is_duplicate(event_id):
    now = time.time()
    for k in [k for k, v in _seen_events.items() if now - v > 300]:
        del _seen_events[k]
    if event_id in _seen_events:
        return True
    _seen_events[event_id] = now
    return False


def post_reply(channel, text, thread_ts=None):
    try:
        slack_client.chat_postMessage(channel=channel, text=text, thread_ts=thread_ts)
    except SlackApiError as e:
        log.error(f"Slack error: {e.response['error']}")


def get_display_name(user_id):
    try:
        return slack_client.users_info(user=user_id)["user"]["real_name"] or user_id
    except Exception:
        return user_id


# ── MESSAGE HANDLER ────────────────────────────────────────────────────────────

def handle_message(text, channel, user, thread_ts):
    clean = re.sub(r"<@[A-Z0-9]+>", "", text).strip()
    if not clean:
        return

    key = (channel, user)

    # Pending ad hoc — user is answering "which team?"
    if key in _pending_adhoc:
        pending = _pending_adhoc.pop(key)
        matched = next((t for t in AD_HOC_TEAMS if t.lower() in clean.lower()), clean.title())
        ticket_id = create_ticket(
            submitted_by=get_display_name(user),
            description=pending["description"],
            category="Data Ad Hoc Request",
            sub_category=matched,
            slack_channel=channel,
            thread_ts=thread_ts,
        )
        cat = CATEGORIES["Data Ad Hoc Request"]
        post_reply(channel,
            f":white_check_mark: Ticket #{ticket_id} created.\n"
            f"*Category:* Data Ad Hoc Request — {matched}\n"
            f"*Assigned to:* {cat['assignee']} ({cat['email']})\n"
            f"*Status:* New",
            thread_ts)
        return

    # New issue
    category = classify_issue(clean)

    if category == "Data Ad Hoc Request":
        _pending_adhoc[key] = {"description": clean, "thread_ts": thread_ts}
        post_reply(channel,
            f":pencil: This looks like a *Data Ad Hoc Request*.\n"
            f"Which team is requesting this? ({', '.join(AD_HOC_TEAMS)})",
            thread_ts)
        return

    ticket_id = create_ticket(
        submitted_by=get_display_name(user),
        description=clean,
        category=category,
        sub_category=None,
        slack_channel=channel,
        thread_ts=thread_ts,
    )
    cat = CATEGORIES[category]
    post_reply(channel,
        f":white_check_mark: Ticket #{ticket_id} created.\n"
        f"*Category:* {category}\n"
        f"*Assigned to:* {cat['assignee']} ({cat['email']})\n"
        f"*Status:* New",
        thread_ts)


# ── API ROUTES ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "chunks": len(_meta)}

@app.get("/tickets")
async def tickets_list():
    return JSONResponse(get_tickets())

@app.patch("/tickets/{ticket_id}/status")
async def update_status(ticket_id: int, request: Request):
    body   = await request.json()
    status = body.get("status", "")
    if status not in TICKET_STATUSES:
        raise HTTPException(400, detail=f"Status must be one of: {TICKET_STATUSES}")
    update_ticket_status(ticket_id, status)
    return {"ok": True, "ticket_id": ticket_id, "status": status}

@app.post("/slack/events")
async def slack_events(request: Request, background_tasks: BackgroundTasks):
    body_bytes = await request.body()
    try:
        body = json.loads(body_bytes)
    except json.JSONDecodeError:
        raise HTTPException(400, detail="Invalid JSON")

    if body.get("type") == "url_verification":
        return JSONResponse({"challenge": body["challenge"]})

    if SLACK_SIGNING_SECRET:
        if not verify_slack_signature(
            body_bytes,
            request.headers.get("X-Slack-Request-Timestamp", ""),
            request.headers.get("X-Slack-Signature", ""),
        ):
            raise HTTPException(403, detail="Invalid signature")

    event_id = body.get("event_id", "")
    if event_id and is_duplicate(event_id):
        return JSONResponse({"ok": True})

    event = body.get("event", {})
    if event.get("bot_id") or event.get("subtype") == "bot_message":
        return JSONResponse({"ok": True})

    if event.get("type") in ("message", "app_mention"):
        background_tasks.add_task(
            handle_message,
            event.get("text", ""),
            event.get("channel", ""),
            event.get("user", "unknown"),
            event.get("thread_ts") or event.get("ts"),
        )

    return JSONResponse({"ok": True})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
