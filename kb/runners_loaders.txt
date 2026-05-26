=== BADGER KB: RUNNERS_LOADERS ===
Scheduled runners, data loaders, sync jobs
============================================================



--- FILE: AVMRunner\AVMRunner\Program.cs ---
namespace AVMRunner
{
    class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string server = args["server"];
            DateTime asOf = args.ContainsFlag("asof") ? args["asof"].AsDate().Value : DateTime.Today;
            string key = args["key"];
            List<int> avms = args.GetArray<int>("avms", '|');

            foreach(int avm in avms)
            {
                int vendor_id = BadgerLib.Valuations.VendorIdFromValuationType(server, avm);


                var apns = BadgerLib.Valuations.GetNeededValuations(server, asOf,avm);

                if (vendor_id == 2) 
                {
                    string client_id = "MV3XgkfH8LVchzYKEycMQXw8DUUb6C3Q";
                    string client_secret = "[REDACTED — retrieve from Azure/IT]";
                    CoreLogicLib.CL cl = new CL(client_id,client_secret);
                    
                    

                   
                    foreach (var apn in apns)
                    {
                        string reference = BadgerLib.Valuations.GetReference(server, avm);
                        string property = Assets.Assets.GetForeignAssetId(server, 2, apn.asset_id);
                        if (null == property)
                        {
                            property = cl.GetPropertyID(apn.address_1, apn.zip);
                            Assets.Assets.RecordForeignIds(server, vendor_id, apn.asset_id, property);
                        }
                        Console.WriteLine($"[{vendor_id}/ AVM #{avm}] - Running: " + property);
                        var value = cl.GetAVMValueInternal(property, reference);
                        Valuations.InsertValidation(server, apn.asset_id, asOf, avm, value.estimatedValue, value.highValue, value.lowValue, null, null, 2, null,value.xml_source);
                    }
                }
            }

        }
    }
}


--- FILE: AVMRunner\AVMRunner\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("AVMRunner")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("AVMRunner")]
[assembly: AssemblyCopyright("Copyright ©  2020")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("04c5e2b0-53f5-42cc-b15c-98dcbee61822")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: AlertRunner\AlertRunner\Program.cs ---
namespace AlertRunner
{
    class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string from = args["from"];
            string server = args["server"];
            
            
            bool email = args.ContainsFlag("email");
            bool markprocessed = args.ContainsFlag("markprocessed");
            string smtp_server = args["smtp_server"];
            string footer = args.ArgIfAvailableNotNull<string>("footer");
            string header = args.ArgIfAvailableNotNull<string>("header");
            bool onlycover = args.ContainsFlag("onlycover");
            bool write_results = args.ContainsFlag("writeresults");
            bool error = false;


            
            
            try
            {
                DataSet tbl = GetAlerts(server, markprocessed, onlycover, false);
                foreach (DataRow row in tbl.Tables[0].Rows)
                {
                    string subject = row["subject"].ToString();
                    string user_mail = row["email"].ToString();
                    string user_sql = String.Format("email = '{0}'", user_mail);
                    string body = "";
                    DataTable user_table = tbl.Tables[1].Select(user_sql).CopyToDataTable();
                    user_table.Columns.Remove("email");



                    if (email)
                    {
                        DataSet set = new DataSet();
                        string headers = "";
                        IEnumerable<string> all_captions = user_table.UniqueValues<string>("caption");
                        foreach (string caption in all_captions)
                        {
                            string u_sql = String.Format("caption = '{0}'", caption.Replace("'", "''"));
                            DataTable t = user_table.Select(u_sql).CopyToDataTable();
                            t.Columns.Remove("caption");
                            set.Tables.Add(t.Copy());
                        }

                        List<IFormatHelper> fh = Database.RRHelper.GetFormats(server);
                        string table_headers = String.Join("|", all_captions);
                        HTMLUtils.HTMLHelper hh = UtilsLib.HTMLUtils.ToHtml(set, null, table_headers, null, fh);
                        
                        

                        if (!String.IsNullOrEmpty(header))
                            body += header;
                        
                        body += "<br><br></small>";
                        body += hh.html;
                        if (!String.IsNullOrEmpty(footer))
                            body += footer;
                        UtilsLib.Mail m = new Mail(from, smtp_server, null, null);

                        
                        m.SendSMTPMail(user_mail, null, "dfoster@rwbaird.com", subject, body, null, true, true, from);
                        
                        Console.WriteLine("Sent mail to: " + user_mail);
                    }

                }
            }
            catch (Exception n)
            {
                UtilsLib.Error.SendDefaultError(n, args.ArgDump, true);
                error = true;
            }
            if(error && write_results)
                GetAlerts(server, markprocessed, onlycover, write_results);
        }

        public static DataSet GetAlerts(string server, bool mark_processed,bool only_cover, bool write_results)
        {
            string sql = "exec dbo.ProcessAlerts @mark_processed = @mark_processed, @only_cover=@only_cover, @write_results=@write_results";
            Query q = new Query(sql, server);
            q.AddParameter("@mark_processed", mark_processed);
            q.AddParameter("@only_cover", only_cover);
            q.AddParameter("@write_results", write_results);
            return q.Execute();
        }
    }
}


--- FILE: AlertRunner\AlertRunner\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("AlertRunner")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("AlertRunner")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2018")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("fc679990-ed05-4c21-b5a0-f3d5c7b2c6a1")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: ReportRunner\ReportRunner\Conversions.cs ---
namespace ReportRunner
{
    
    
        
    
}


--- FILE: ReportRunner\ReportRunner\Program.cs ---
namespace ReportRunner
{
    class Program
    {

        static void Main(string[] args_raw)
        {
            {
                CommandLineArgs args = new CommandLineArgs(args_raw);

                if (!args.ContainsFlag("show"))
                    UtilsLib.Windows.MinimizeActiveProcessWindow();

                Mail.MailServerConfig mp = new Mail.MailServerConfig
                {
                    server = args.ArgIfAvailableNotNull<string>("smtp_server"),
                    user = args.ArgIfAvailableNotNull<string>("smtp_user"),
                    pass = args.ArgIfAvailableNotNull<string>("smtp_pass"),
                    port = args.ArgIfAvailableNotNull<int>("smtp_port", 25)
                };

                
                string env = args.ContainsFlag("env") ? args["env"] : "PROD";
                Constants.SetEnvironment(Constants.GetEnvironment(env));

                if (args.ContainsFlag("mailprofile"))
                    mp = UtilsLib.Mail.MailProfiles.GetProfiles()[args["mailprofile"]];
                
                string from = args["from"];

                string to = args.ArgIfAvailableNotNull<string>("to");
                string cc = args.ArgIfAvailableNotNull<string>("cc");
                string bcc = args.ArgIfAvailableNotNull<string>("bcc");

                string validateerroremails = args.ArgIfAvailableNotNull<string>("validatemails");
                string validatesql = args.ArgIfAvailableNotNull<string>("validatesql");
                Nullable<int> validaterowcount = args.ArgIfAvailableNotNull<int>("validaterowcount");

                string subject = args.ContainsFlag("subject")
                    ? UtilsLib.Clean.CommonVariables(args["subject"], "/")
                    : null;
                string body = args.ContainsFlag("body") ? args["body"] : "";
                string sql = args.ContainsFlag("sql") ? args["sql"] : null;
                string tables = args.ContainsFlag("tables") ? args["tables"] : null;
                string database_server = args["server"];
                string vars_html = args.ContainsFlag("vars_html") ? args["vars_html"] : null;
                string header_args = args.ContainsFlag("headers") ? args["headers"] : null;
                bool only_biz_day = args.ContainsFlag("onlybizday");
                bool only_last_bday_month = args.ContainsFlag("only_last_bday_month");
                string specific_day = args.ContainsFlag("specificday") ? args["specificday"] : null;
                bool smtp = args.ContainsFlag("smtp");
                string header = args.ContainsFlag("header") ? args["header"] : null;
                bool as_is = args.ContainsFlag("as_is");

                MailPriority mailpriority = MailPriority.Normal;
                if (args.ContainsFlag("mailpriority"))
                    mailpriority = (args["mailpriority"].ToUpper() == "HIGH" ? MailPriority.High : MailPriority.Low);
                                
                IEnumerable<int> excel_tables = null;
                if (args.ContainsFlag("exceltable"))
                    excel_tables = args["exceltable"].Split('|').Select(int.Parse);
                else if (args.ContainsFlag("exceltables"))
                    excel_tables = args["exceltables"].Split('|').Select(int.Parse);
                
                string base_name = args.ContainsFlag("excelname") ? args["excelname"] : "QuickExport";

                List<string> excel_table_tab_names = args.ContainsFlag("exceltabnames") ? args["exceltabnames"].Split('|').ToList() : null;
                UtilsLib.Excel.EXCEL_FILE_FORMAT_SIMPLE output_fmt = args.ContainsFlag("excelfmt") ? UtilsLib.Excel.GetXLFileFormatSimple(args["excelfmt"]) : Excel.EXCEL_FILE_FORMAT_SIMPLE.XLSB;

                string email_body_range = args.ContainsFlag("emailbodyrange") ? args["emailbodyrange"] : null;

                bool pdf = args.ContainsFlag("pdf");

                
                bool slack_subject = args.ContainsFlag("slacksubject");
                List<string> slack_table = args.ContainsFlag("slacktable") ? args["slacktable"].Split('|').ToList() : null;

                UtilsLib.ProcessHelper.ClearClipboardAnyThread();

                Dictionary<string, object> vars = null;
                if (args.ContainsFlag("vars"))
                {
                    vars = args.GetDictionary<object>(args["vars"]);
                    subject = UtilsLib.Clean.ApplyDictionary<object>(vars, subject, "/");
                    tables = UtilsLib.Clean.ApplyDictionary<object>(vars, tables, "/");
                }

                if (only_biz_day)
                {
                    UtilsLib.Dates.XDateTime d = new Dates.XDateTime(DateTime.Today);
                    if (!d.IsWorkDay)
                    {
                        Console.WriteLine("Not a business day...exiting.");
                        return;
                    }
                }

                if (only_last_bday_month)
                {
                    UtilsLib.Dates.XDateTime d = new Dates.XDateTime(DateTime.Today);
                    if (d.LastBizDayOfMonth() != DateTime.Today)
                    {
                        Console.WriteLine("Not the last business day of month...exiting.");
                        return;
                    }
                }

                if (!specific_day.IsNullOrEmpty())
                {
                    DateTime d = DateTime.Today;
                    DayOfWeek day;
                    int dayOfMonth;
                    if (specific_day.Contains("day"))
                    {
                        if (Enum.TryParse<DayOfWeek>(specific_day, true, out day))
                        {
                            if (day != DateTime.Today.DayOfWeek)
                            {
                                Console.WriteLine("Not the specified day of the week...exiting.");
                                return;
                            }
                        }
                    }
                    else if ((int.TryParse(specific_day, out dayOfMonth) && dayOfMonth != 0))
                    {
                        try { d = d.SetDay(dayOfMonth); }
                        catch { Console.WriteLine("Invalid day of the month"); return; }
                        if (!DateTime.Today.SameDay(d.Date))
                        {
                            Console.WriteLine("Not the specified day of the month...exiting.");
                            return;
                        }
                    }
                }

                List<string> attachments = new List<string>();
                Mail m = new Mail(mp);
                DataSet results = null;
                XL.XLHelper xl = null;
                string filename = null;
                string html_body = body;
                List<object> var_list = new List<object>();
                string slackMessage = null;
                bool slackMessageSet = false;

                if (null != validatesql)
                {
                    Query q = new Query(validatesql, database_server);
                    q.ApplyCommonVariables();
                    q.AddParameterDictionary<object>(vars, null);
                    DataTable t = q.ExecuteTable();
                    if (t.Rows.Count != validaterowcount)
                    {
                        if (null == validateerroremails)
                            validateerroremails = to;
                        m.SendMail(validateerroremails, null, null, "REPORT FAILED VALIDATION: " + subject, null, null);
                        return;
                    }
                }

                if (null != sql)
                {
                    Query q = new Query(sql, database_server);
                    q.ApplyCommonVariables();
                    q.AddParameterDictionary<object>(vars, null);
                    results = q.Execute();

                    int tbl_no = 0;

                    
                    if (args.ContainsFlag("cols"))
                        results = results.CopyAndTrimColumns(args["cols"]);

                    foreach (DataTable tbl in results.Tables)
                    {
                        subject = UtilsLib.Clean.ApplySimpleVariable<int>("@rows[" + tbl_no + "]", results.Tables[tbl_no].Rows.Count, subject);
                        tables = UtilsLib.Clean.ApplySimpleVariable<int>("@rows[" + tbl_no + "]", results.Tables[tbl_no].Rows.Count, tables);
                        int row_num = 0;
                        if (subject.ToUpper().Contains("@VALUES") || (slack_table != null && slack_table.Count > 0))
                        {
                            foreach (DataRow row in tbl.Rows)
                            {
                                int col_num = 0;
                                foreach (DataColumn col in tbl.Columns)
                                {
                                    string var_name = $"@values[{row_num}][{col_num}]";


                                    if (subject.Contains(var_name))
                                    {
                                        object value = row[col];
                                        string val_obj = value.ToString();
                                        string clean_html = UtilsLib.Clean.HtmlFormat(col, value);
                                        subject = subject.Replace(var_name, clean_html);
                                    }

                                    if (!slackMessageSet && slack_table != null && slack_table.Count > 0 && col_num == 0)
                                    {
                                        object value = row[0];
                                        slackMessage = UtilsLib.Clean.HtmlFormat(col, value);
                                        slackMessageSet = true;
                                    }
                                    col_num++;
                                }
                                row_num++;
                            }
                        }
                        tbl_no++;
                    }

                    if (null != results && results.Tables.Count > 0 && null != results.Tables[0])
                    {
                        subject = UtilsLib.Clean.ApplySimpleVariable<int>("@total", results.Tables[0].Rows.Count, subject);
                        tables = UtilsLib.Clean.ApplySimpleVariable<int>("@total", results.Tables[0].Rows.Count, tables);
                    }

                    if (args.ContainsFlag("excel") || (args.ContainsFlag("excelonlyifpopulated") && results.Tables[0].Rows.Count > 0))
                    {
                        List<DataTable> tbls = new List<DataTable>();
                        int s = 0;
                        if (null == excel_tables)
                            excel_tables = new int[] { 0 };
                        foreach (int i in excel_tables)
                        {
                            DataTable t = results.Tables[i].Copy();
                            if (null != excel_table_tab_names)
                                t.TableName = excel_table_tab_names[s];
                            tbls.Add(t);
                            s++;
                        }

                        base_name = UtilsLib.Clean.CommonVariables(base_name, null, null);
                        base_name = UtilsLib.FileLib.GenerateQuickNameFull(null, base_name, vars);
                        FieldLib.Fields f = new FieldLib.Fields(database_server, Database.FieldHelper.GetFieldTableInternal);
                        string final_name;
                        if (as_is)
                            final_name = UtilsLib.Excel.CreateQuickExcel(base_name, tbls, false, output_fmt, true, f);
                        else
                            final_name = UtilsLib.Excel.CreateQuickExcel(base_name, tbls, true, output_fmt, true, f);
                        UtilsLib.FileLib.WaitForFile(final_name, 5000);
                        attachments.Add(final_name);
                    }

                    if (args.ContainsFlag("onlytables"))
                    {
                        List<DataTable> keep = new List<DataTable>();
                        foreach (string s in args["onlytables"].Split('|'))
                        {
                            int zero_based_index = System.Convert.ToInt32(s);
                            keep.Add(results.Tables[zero_based_index]);
                        }

                        List<DataTable> removes = new List<DataTable>();
                        for (int i = 0; i != results.Tables.Count; i++)
                        {
                            DataTable tbl = results.Tables[i];
                            if (!keep.Contains(tbl))
                                removes.Add(tbl);
                        }

                        for (int i = 0; i != removes.Count; i++)
                        {
                            DataTable remove = removes[i];
                            results.Tables.Remove(remove);
                        }
                    }

                    int blank_table = 0;
                    bool one_populated = false;

                    if (args.ContainsFlag("onlyblanktable"))
                        blank_table = System.Convert.ToInt32(args["onlyblanktable"]);
                    
                    if (args.ContainsFlag("onlyblank") && results.Tables[blank_table].Rows.Count != 0)
                        return;
                    

                    if (args.ContainsFlag("anypopulated"))
                    {
                        foreach (DataTable t in results.Tables)
                        {
                            if (t.Rows.Count != 0)
                                one_populated = true;
                        }

                        if (!one_populated)
                            return;
                    }

                    if (args.ContainsFlag("anypopulatedintables"))
                    {
                        one_populated = false;
                        foreach (string s in args["anypopulatedintables"].Split('|'))
                        {
                            int zero_based_index = System.Convert.ToInt32(s);
                            if (results.Tables[zero_based_index].Rows.Count != 0)
                                one_populated = true;
                        }
                        if (!one_populated)
                            return;
                    }

                    if (args.ContainsFlag("onlynonblank"))
                    {
                        bool all_blank = results.Tables[blank_table].Rows.Count == 0;
                        if (all_blank)
                            return;
                    }

                    if (args.ContainsFlag("htmltables"))
                    {
                        List<IFormatHelper> fh = Database.RRHelper.GetFormats(database_server);
                        HTMLUtils.HTMLHelper hh = UtilsLib.HTMLUtils.QuickToHtml(results.Tables[0], vars_html, header_args, tables, fh);
                        html_body = hh.html;
                        var_list = hh.var_list;
                    }
                }

                if (null == xl && args.ContainsFlag("template"))
                {
                    filename = Path.Combine(
                        System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().CodeBase
                            .Replace("file:
                    xl = new XL.XLHelper(null);
                    xl.CreateNewApp(true);
                    xl.ToggleAppVisible(true);
                }

                if (args.ContainsFlag("template"))
                {
                    xl.ToggleCalcs(XL.XLHelper.XLCalcMode.MANUAL);

                    if (args.ContainsFlag("addins"))
                    {
                        Console.WriteLine("Loading Addin: " + args["addins"]);
                        xl.LoadAddins(args["addins"]);
                    }

                    if (args.ContainsFlag("refresh"))
                    {
                        Console.WriteLine("Refreshing All Queries");
                        xl.RefreshAllQueries();
                    }

                    if (args.ContainsFlag("excelconfig"))
                    {
                        string[] pair = args["excelconfig"].Split(';');
                        foreach (string s in pair)
                        {
                            string range = s.Split('|')[0];
                            int table = System.Convert.ToInt32(s.Split('|')[1]);
                            
                            xl.ClearRangeContents(null, range, true);
                            
                            xl.WriteRange(range, results.Tables[table], true);
                        }
                    }

                    Console.WriteLine("Calculating...");
                    xl.FullForceCalc();

                    if (args.ContainsFlag("wait"))
                        System.Threading.Thread.Sleep(System.Convert.ToInt32(args["wait"]) * 1000);

                    if (args.ContainsFlag("macro"))
                    {
                        Console.WriteLine("Running Macro: " + args["macro"]);
                        xl.RunMacro(args["macro"]);
                    }

                    if (pdf)
                    {
                        string sheets = args["pdf"];
                        base_name = UtilsLib.FileLib.GenerateQuickNameFull(subject, base_name, vars);
                        string pdf_name = base_name + ".pdf";
                        xl.SaveWorksheetsAsPDF(sheets, pdf_name, false);
                        attachments.Add(pdf_name);
                    }

                    if (args.ContainsFlag("save"))
                    {

                        Console.WriteLine("Saving Original File");
                        

                        string new_filename = UtilsLib.Clean.ApplyDictionary<string>(null, subject, "/");
                        new_filename = UtilsLib.Clean.CleanFilename(new_filename, true);
                        string directory = Path.GetDirectoryName(filename);
                        directory = Path.GetTempPath();
                        string new_filename_full = Path.Combine(directory, new_filename) + ".xlsb";
                        
                        xl.SaveActiveWorkbookAs(new_filename_full, true);
                        filename = new_filename_full;
                    }

                    if (args.ContainsFlag("emailbodyrange"))
                    {
                            html_body = null;
                            xl.CopyRangeToClipboard(null, email_body_range);                      
                    }

                    if (args.ContainsFlag("generatehtmlbody"))
                    {
                        string temp_file = xl.ActiveWorkbookName().Replace(".xlsm", "").Replace(".xls", "") + ".html";
                        string gen_filename = xl.SaveHTML(null);
                        html_body = System.IO.File.ReadAllText(gen_filename);
                        html_body = html_body.Replace("�", "");
                        html_body = UtilsLib.HTMLUtils.InlineCSS(html_body);
                    }

                    if (args.ContainsFlag("exportsheets")) 
                    {
                        System.Console.WriteLine("Waiting to attach file...");
                        System.Threading.Thread.Sleep(5000);
                        XL.XLHelper xlh = new XL.XLHelper(null);
                        int process_id = xl.ProcessId();
                        xlh.SetApplicationFromPID(process_id);
                        base_name = UtilsLib.FileLib.GenerateQuickNameFull(subject, base_name, vars) + ".xlb";
                        xlh.ExportSheetsBETA(args["exportsheets"].Split('|').ToList(), base_name, false, XL.XLHelper.EXCEL_FILE_FORMAT_SIMPLE.XLSB, false);
                        attachments.Add(base_name);
                     }
                }

                if (args.ContainsFlag("attach"))
                {
                    System.Console.WriteLine("Waiting to attach file...");
                    foreach (string s in args["attach"].Split("|"))
                    {
                        UtilsLib.FileLib.WaitForFile(s, 5000);
                        attachments.Add(s);
                    }
                }

                if (args.ContainsFlag("nosend"))
                {
                    return;
                }

                if (null != subject)
                {
                    if (null != header)
                    {
                        if (header.ToLower().Contains(".jpg") || header.ToLower().Contains(".png"))
                            html_body = html_body.Insert(0,
                                String.Format("<center><img src=\"{0}\"></center>", header));
                        else
                        {
                            if (File.Exists(header))
                                header = File.ReadAllText(header);
                            else if (header.Contains("<") && header.Contains("</"))
                            {
                                header = header;
                            }
                            else
                            {
                                header = "<font face = \"verdana\" size=1>" + header + "</font>";
                            }

                            html_body = html_body.Insert(0, header);
                        }
                    }


                    if (args.ContainsFlag("footer"))
                    {
                        html_body += "<br><br>";
                        string footer = args["footer"];
                        footer = UtilsLib.Clean.ApplyDictionary<object>(vars, footer, "/");
                        if (File.Exists(footer))
                            html_body += File.ReadAllText(args["footer"]);
                        else
                            html_body += footer;
                    }

                    Console.WriteLine($"Sending Mail: {String.Join(",", to)} / CC: {String.Join(",", cc)} / BCC: {String.Join(",", bcc)} ");
                    if (smtp)
                        m.SendSMTPMail(to, cc, bcc, subject, html_body, attachments, true, true, from, mailpriority);
                    else
                    {
                        if (args.ContainsFlag("outlookalt"))
                            UtilsLib.Mail.CreateOutlookMail(subject, null, attachments, to?.Split(';'), cc?.Split(';'), bcc?.Split(';'), false, null, true, true, true, null, null);
                        else
                            m.SendMail(to, cc, bcc, subject, html_body, attachments);
                    }

                    if (slackMessageSet && !string.IsNullOrEmpty(slackMessage) && slack_table != null && slack_table.Any())
                    {
                        string slackFinalMessage = slackMessage;
                        if (slack_subject)
                            slackFinalMessage = subject + "\n" + slackMessage;

                        SClient sc = new SClient();
                        foreach (string rec in slack_table)
                        {
                            bool isDefined = Enum.IsDefined(typeof(SClient.RECIPIENT), rec);
                            if (isDefined)
                            {
                                SClient.RECIPIENT recipient = (SClient.RECIPIENT)Enum.Parse(typeof(SClient.RECIPIENT), rec);
                                sc.SendMessage(recipient, slackFinalMessage);
                            }
                        }
                    }
                    
                    if (null != xl)
                    {
                        xl.CloseWorkbook(null, false);
                        xl.Quit();
                    }
                }

                UtilsLib.ProcessHelper.ClearClipboardAnyThread();
            }
        }

    }
}


--- FILE: ReportRunner\ReportRunner\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("ReportRunner")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("ReportRunner")]
[assembly: AssemblyCopyright("Copyright ©  2013")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("eb79d59b-d722-47fa-b35e-ce7a9010bb1c")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: ReportRunner\ReportRunner\SQL\ActiveCountiesMissingInfo.sql ---
SELECT c.state, c.county FROM Counties c WHERE c.ACTIVE=0 AND CONCAT(c.state, ' ', c.county) in (select distinct CONCAT(a.state, ' ', a.county) from vAssetsEx a where a.final_disposition_date is null)
SELECT c.state, c.county FROM Counties c WHERE c.ACTIVE=1 AND c.tax_website is NULL order by c.state,c.county


--- FILE: ReportRunner\ReportRunner\SQL\AgedFundedAssetsQuery.sql ---
DECLARE @ageThreshold int = 15

SELECT 
  f.asset_id 
  ,a.name_simple
  ,a.address_simple
  ,FORMAT(f.value_date,'MM-dd-yyyy') [VALUE_DATE]
  ,DATEDIFF(day,f.value_date,dbo.TodayNY()) [DAYS_ON_LINE]
  ,t.settle_date 
  ,a.account
FROM vFundings_New f 
  JOIN vAssetsPositionEx a on f.asset_id = a.asset_id 
  JOIN vTradesEx t on t.asset_id = f.asset_id 
  JOIN vAccountsEx act on a.account_id = act.account_id
 WHERE f.funding_status != 'Cancelled' and f.funding_type = 'Deal'
 and DATEDIFF(day,f.value_date,dbo.TodayNY()) >= @ageThreshold
 and t.settle_date < dbo.TodayNY() 
 and act.is_financing_acct = 1
order by DATEDIFF(day,f.value_date,dbo.TodayNY()) desc


--- FILE: ReportRunner\ReportRunner\SQL\AssetsWithUOO.sql ---
select e.asset_id,a.name_simple,sum(e.amount) [amount_due_$] from vExpensesEx e
join vAssetsPositionEx a on e.asset_id = a.asset_id
where e.unpaid_owner_obligation=1 and e.repaid_by_owner=0 and a.final_disposition_date is null
group by e.asset_id,a.name_simple,a.account

select e.asset_id,a.name_simple,sum(e.amount) [amount_due_$],max(a.final_disposition_date) [final_disposition_date],a.account,e.reimbursable,e.status,e.investor_expense_status from vExpensesEx e
join vAssetsPositionEx a on e.asset_id = a.asset_id
where e.unpaid_owner_obligation=1 and e.repaid_by_owner=0 and a.final_disposition_date is not null and a.account != 'UPS BUYBACK'
group by e.asset_id,a.name_simple,a.account,e.reimbursable,e.status,e.investor_expense_status


--- FILE: ReportRunner\ReportRunner\SQL\Assets_Without_Owner_Mapping.sql ---
selecT id, update_time, update_by, address_simple, applicant_id, applicant_co_id 
from Assets a 
where not exists (select * from AssetApplicantMap aam where a.id = aam.asset_id and aam.applicant_id = a.applicant_id and aam.applicanttype_id=1) or (a.applicant_co_id is not null and not exists (select * from AssetApplicantMap aam where a.id = aam.asset_id and aam.applicant_id = a.applicant_co_id and aam.applicanttype_id=2))


--- FILE: ReportRunner\ReportRunner\SQL\AvailableCollateralBarclayFundingSummary.sql ---
select count(ex.asset_id) [num trades], sum(ex.investment_payment) [total investment payment_$], sum(ex.[advance_amount]) [total barcap advance_$]
from vAvailableCollateralEx ex

select ex.asset_id
  ,ex.has_open_negam_io_mtg [negam io mtg]
  ,ex.lien_position [lien position]
  ,ex.credit_score [orig credit score_]
  ,ex.credit_score_calc_current [curr credit score_]
  ,ex.secured_debt [secured debt_$]
  ,ex.exercise_value_cutoff [exercise val cutoff_$]
  ,ex.exchange_rate [exchange rate]
  ,ex.starting_home_value [starting home value_$]
  ,ex.investment_payment [investment payment_$]
  ,ex.total_home_finance [thf]
  ,ex.effective_date [effective date] 
  ,ex.collat_status [collat status]
  ,ex.[advance_rate] [barclays advance rate_%]
  ,ex.[advance_amount] [barclays advance_$]
  ,ex.[msg] [advance_msg]
  from dbo.vAvailableCollateralEx ex


--- FILE: ReportRunner\ReportRunner\SQL\AVMUpdates.sql ---
drop table if exists #t
drop table if exists #r

declare @latest date
select @latest=max(asOf) from Valuations

select
  v.asset_id
  , v.valuationtype_id
  , max(v.asOf) [prior_latest]
  into #t
  from
    Valuations v
  where
    v.asOf < @latest
  group by 
    v.asset_id
    , v.valuationtype_id


select 
  a.asset_id
  , a.address_simple
  , a.name_simple
  , v.value [value]
  , p.value [value_prev]
  , v.value-p.value [delta]

  , v.value-a.starting_home_value [delta_from_origination]

  , vt.[name]
  , ven.name [vendor_name]
  , a.investment_payment
  into #r
  from 
    Valuations v
    join vAssetsEx a on a.asset_id = v.asset_id
    join ValuationTypes vt on v.valuationtype_id = vt.id
    left join #t t on v.asset_id = t.asset_id and t.valuationtype_id=V.valuationtype_id
    left join Valuations p on p.asset_id = T.asset_id and t.valuationtype_id = p.valuationtype_id and p.asOf = t.prior_latest
    left join Vendors ven on ven.id = vt.vendor_id
  where
    v.asOf = @latest
  ORDER BY
    A.NAME_SIMPLE desc
    , vt.[name]
    
       
   select
     count(*) [count]
     , [NAME]
     , VENDOR_NAME
     , sum(r.delta * r.investment_payment) / sum(r.investment_payment) [avg_delta_prior_run_$]
     
     from #R r
      where
        r.value is not null
        and r.value_prev is not null
     GROUP BY
       [NAME]
      , VENDOR_NAME
      
     order by
      [name]
      , [VENDOR_NAME]
     
     
     
   select
     count(*) [count]
     , [NAME]
     , VENDOR_NAME
     from #R
     GROUP BY
       [NAME]
      , VENDOR_NAME
      
     order by
      [name]
      , [VENDOR_NAME]
     
     
   select
    asset_id
    , address_simple
    , [value] [value_$]
    , [value_prev] [value_prev_$]
    , [delta] [delta_$]
    , null [ ]
    , [delta_from_origination] [delta_from_origination_$]
    , null [   ]
    , [name]
    from
     #r
     
     

    
    drop table #t
    drop table #r


--- FILE: ReportRunner\ReportRunner\SQL\BadCreditMapping.sql ---
drop table if exists #tmp
drop table if exists #next 

declare @last_run date
select @last_run = max(asOf) from vCreditLoads where note is null and update_by = 'dan@unlock.com'

select
count(*) [count]
,lender_name
,cr_creditor
into #tmp
from
vDebtEx d
  join vAssets a on a.asset_id = d.asset_id
where
  effective_date <= dateadd(d,-3,@last_run)
  and d.cr_visible = 1
group by 
lender_name
,cr_creditor


select t.* into #next from (select count(*) [count],cr_creditor from #tmp t group by cr_creditor having count(*)>1) s join #tmp t on t.cr_creditor=s.cr_creditor

select d.debt_id,d.lender_id,d.asset_id,name_simple,d.lender_name,d.cr_creditor from vDebtEx d join vAssetsEx a on d.asset_id = a.asset_id join #next n on d.lender_name = n.lender_name and d.cr_creditor = n.cr_creditor order by cr_creditor,lender_name

drop table if exists #tmp
drop table if exists #next


--- FILE: ReportRunner\ReportRunner\SQL\BalUsage.sql ---
drop table if exists #tmp
drop table if exists #pending

declare @funded_not_originated float = 0 
declare @sold_not_settled float = 0 
declare @originated_not_sold float = 0 


declare @guideline_id int

select @guideline_id = guideline_id_latest from vAccounts a where a.account_id = @account_id

SELECT 
  f.customer_pipeline_label
  , f.investment_payment 
  , f.effective_date
  , f.funding_date
  , p.estimated_signing 
  , p.exception
  into #pending 
  FROM 
    vFundings f
    left join Pipeline p on p.[name] = f.customer_pipeline_label
    
  where 
  originated = 0 and f.funding_date is not null
  

  
  
select @funded_not_originated=sum(investment_payment) from #pending
set @funded_not_originated = case when @funded_not_originated is null then 0 else @funded_not_originated end

select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , a.investment_payment
  , a.investment_payment*1.06 [potential_proceeds_106]
  , null [_]
  , null [__]
  , a.effective_date
  , c.cert_status
  , aeg.exception_desc
  into #tmp
  from 
    vAssetsEx a
    left join vPositions t ON a.asset_id = t.asset_id
    left join vCollatInv c on c.latest = 1 and t.asset_id = c.asset_id
    left join vAssetExceptionsAgg aeg on aeg.asset_id = a.asset_id and aeg.guideline_id = @guideline_id 
  where
    
    a.final_disposition_date is null
    and (t.is_unlock = 1 or t.last_trade is null)
    
    
 SELECT * into #sns FROM vTradesEx t where t.is_settled = 0 and is_unlock = 1
 select @sold_not_settled = sum(investment_payment) from #sns


select @originated_not_sold = isnull(sum(investment_payment),0) from #tmp
select @sold_not_settled = isnull(@sold_not_settled,0)
select @originated_not_sold = isnull(@originated_not_sold,0)

 
  select
    @funded_not_originated [funded_not_orig._$]
    , @originated_not_sold [orig._not_sold_$]
    , @sold_not_settled [sold_not_settled_$]
    , @sold_not_settled+@funded_not_originated+@originated_not_sold [total_b/s usage_$]
    , (@sold_not_settled+@funded_not_originated+@originated_not_sold)*1.06 [total_$_@_106%_$]
    , null [_]
    , (@sold_not_settled+@funded_not_originated+@originated_not_sold)*.09 [total_rev_@_9%_$]
    
    
select
  s.asset_id
  , s.name_simple
  , s.address_simple
  , s.investment_payment [investment_payment_$]
  , s.total_proceeds [total_proceeds_$]
  , null [_]
  , null [__]
  , s.settle_date
  , c.cert_status
  , aeg.exception_desc
  from 
    #sns s
    left join vCollatInv c on c.asset_id = S.asset_id and c.latest = 1
    left join vAssetExceptionsAgg aeg on aeg.asset_id = s.asset_id and aeg.guideline_id=@guideline_id
  


  select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , a.investment_payment [investment_payment_$]
  , potential_proceeds_106 [potential_proceeds_106_$]
  , [_]
  , [__]
  , a.effective_date
  , cert_status
  , exception_desc
    from #tmp a
    order by effective_date ASC

    
  SELECT
    effective_date
    , customer_pipeline_label
    , funding_date
    , investment_payment
    , investment_payment * 1.06 [potential_proceeds_106_$]
    , estimated_signing
    , exception
  FROM
    #pending p
  order by estimated_signing asc
 
 
 select sum(case when cert_status is null then investment_payment else 0 end) [pending_usb_cert_$],sum(case when cert_status is not null then investment_payment else 0 end) [ready_for_sale_$], sum(investment_payment) [total_funded_plus_sold_not_settled_$] from #tmp t 
  
  drop table #tmp
  drop table #sns


--- FILE: ReportRunner\ReportRunner\SQL\BAUItems.sql ---
select 
  a.asset_id
  , a.name_simple
  
  , n.note
  , status
  , priority
  , last_update
  , n.update_by
  from 
    vNotesEx n
    join vAssetsEx a on a.asset_id = n.asset_id
  where
    
    (priority_rank not IN (1,2) or n.priority_rank is null)
    AND (@hours_back = 0 or (datediff(hh,last_update,GetDate()) <= @hours_back))


--- FILE: ReportRunner\ReportRunner\SQL\BorrowingBase.sql ---
exec dbo.BorrowingBaseCalc


--- FILE: ReportRunner\ReportRunner\SQL\BulkFundingEmail.sql ---
drop table if exists #tmp
  
	
	SELECT APP.EXTERNAL_ID, STRING_AGG(concat(FIRST_NAME, ' ',LAST_NAME), ' & ') [FULL_NAME]
	INTO #tmp FROM API_APPLICATION APP
	LEFT JOIN api_applicationprofile app_pro ON app.ID =app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL 
	LEFT JOIN api_profile pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
	WHERE convert(varchar(50),app.EXTERNAL_ID) IN (select asset_id FROM WSFS_Fundings WHERE ValueDate=dbo.TodayNY())
  GROUP BY APP.EXTERNAL_ID;
  
SELECT COUNT(*) [Num_of_Assets], SUM(c.net_wire_amt)[Sum_of_Wires], SUM(c.investment_payment)[Sum_of_Inv_Payments] FROM vClosingEx c join WSFS_Fundings f on c.asset_id = f.Asset_id WHERE f.ValueDate=dbo.TodayNY();

  
  WITH expenses as
  (  
  SELECT APP.external_id,CASE WHEN dbo.ProperCase(exp.paid_to)='Accurategroup' then 'Accurate Group' else dbo.ProperCase(exp.paid_to) end as [appraisal_vendor],exp.amount [appraisal_fee],ROW_NUMBER() OVER(PARTITION BY APP.external_id ORDER BY exp.amount) AS RowNumber
  FROM API_APPLICATION APP
	LEFT JOIN api_applicationprofile app_pro ON app.ID =app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL 
	LEFT JOIN api_profile pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
  LEFT JOIN API_EXPENSE exp on exp.application_id = app.id
	WHERE exp.name like 'Appraisal%' and convert(varchar(50),app.EXTERNAL_ID) IN (select c.asset_id FROM vClosingEx c join WSFS_Fundings f on c.asset_id = f.Asset_id WHERE f.ValueDate=dbo.TodayNY())
  GROUP BY APP.external_id, dbo.ProperCase(exp.paid_to),exp.amount
  )
  SELECT
  'Trade' as [Record Type (Trade / Fee)]  
  ,'New' as [Upload Mode (New / Update / Void)]
  ,NULL as [Prime Broker Account ID]
  ,'Unlock Technologies, Inc.' as [Portfolio (Mandatory for Trade)]
  ,'Unlock Partnership Solutions Inc (Main)' as [Designated Account (Mandatory for Trade)]
  ,'UNLUPS00_First Republic (80009175797)' as [Custodian Account (Mandatory for Trade)]
  ,'First Republic Bank' as [Custodian (Mandatory for Trade)]
  ,NULL as [Trade Reference (Mandatory for Trade / Fee)]
  ,dbo.TodayNY() as [Trade Date (Mandatory for Trade)]
  ,dbo.TodayNY() as [Settlement Date (Mandatory for Trade)]
  ,NULL as [Trader]
  ,NULL as [Strategy]
  ,NULL as [Sub Strategy]
  ,'Do Not Send' as [Send To Prime Broker (Send / Do Not Send / Yes / No)]
  ,NULL as [Comments]
  ,'B' as [Buy Sell (B-Buy/S-Sell/BC-Buy Cover/SS-Sell Short) (Mandatory for Trade)]
  ,c.INVESTMENT_PAYMENT as [Quantity (Mandatory for Trade)]
  ,1 as [Price (Mandatory for Trade)]
  ,NULL as [Clearing Mode]
  ,'ClearEdge Title, Inc' as [Counter Party Dealer (Mandatory for Trade)]
  ,'USD' as [Trade Currency (Mandatory for New Security)]
  ,'P' as [Settle Currency Ind (P-Portfolio /L-Local / O-Other)]  
  ,'USD' as [Settle Currency Type]
  ,NULL as [Currency Exchange FXRate]
  ,'Equity' as [Asset Class (Mandatory for New Security)]
  ,dbo.ProperCase(CONCAT(p.address, ' (',#tmp.FULL_NAME,')')) as [Security Name]
  ,'Other' as [Security Reference Type (Mandatory for New Security)]
  ,c.ASSET_ID as [Security Reference (Mandatory for Trade)]
  ,'United States' as [Exchange (Mandatory for New Security)]
  ,NULL as [Sector]
  ,NULL as [Sub Sector]
  ,NULL as [Fee Type (Mandatory for Fee)]
  ,NULL as [Amount (Mandatory for Fee)]
  ,NULL as [Currency Type Code (Mandatory for Fee)]
  ,NULL as [Fee FX Rate]
  ,NULL as [Security Reference Type 2]
  ,NULL as [Security Reference 2]
  ,NULL as [Execution Platform]
  ,NULL as [Custom Tag (e.g. CustomGroup1: CustomTag1, CustomTag2; CustomGroup2: CustomTag3)]
  ,NULL as [BBGYellow Key]
  ,NULL as [Trade Journal YN]
  ,NULL as [Journal Category]
  ,NULL as [Include In Settlement (1 - Yes, 0 - No)]
  ,NULL as [Execution Methodology (e.g. EM1; EM2)]
  ,NULL as [Send To Fund Administrator (Send / Do Not Send / Yes / No)]
  ,NULL as [Override Cost Date]
  ,dbo.ProperCase(p.address) as [Homeowner Address]
  ,expense1.appraisal_vendor as [Appraisal Vendor]
  ,expense1.appraisal_fee as [Appraisal Fee Amount]
  ,expense2.appraisal_vendor as [Appraisal Vendor (2nd)]
  ,expense2.appraisal_fee as [Appraisal Fee Amount (2nd)]
  ,expense.amount as [Origination Fee]
  ,c.net_wire_amt as [Total Wire Amount]
  ,c.file_num as [File Number]
  ,#tmp.FULL_NAME [Property Owner(s)]
  FROM vClosingEx c
  JOIN vPipeline p on p.asset_id=c.asset_id
  JOIN #tmp on c.asset_id=convert(varchar(50),#tmp.EXTERNAL_ID)
  LEFT JOIN expenses as expense1 on c.asset_id=convert(varchar(50),expense1.EXTERNAL_ID) and expense1.RowNumber=1
  LEFT JOIN expenses as expense2 on c.asset_id=convert(varchar(50),expense2.EXTERNAL_ID) and expense2.RowNumber=2
  LEFT JOIN API_EXPENSE expense ON (convert(bigint,p.application_id) = expense.application_id and expense."TYPE" ='origination_charge')
  
  JOIN WSFS_Fundings f on c.asset_id = f.Asset_id 
  WHERE f.ValueDate=dbo.TodayNY();
  
  
    WITH expenses as
  (  
  SELECT APP.external_id,CASE WHEN dbo.ProperCase(exp.paid_to)='Accurategroup' then 'Accurate Group' else dbo.ProperCase(exp.paid_to) end as [appraisal_vendor],exp.amount [appraisal_fee],ROW_NUMBER() OVER(PARTITION BY APP.external_id ORDER BY exp.amount) AS RowNumber
  FROM API_APPLICATION APP
	LEFT JOIN api_applicationprofile app_pro ON app.ID =app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL 
	LEFT JOIN api_profile pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
  LEFT JOIN API_EXPENSE exp on exp.application_id = app.id
	WHERE exp.name like 'Appraisal%' and convert(varchar(50),app.EXTERNAL_ID) IN (select c.asset_id FROM vClosingEx c join WSFS_Fundings f on c.asset_id = f.Asset_id WHERE f.ValueDate=dbo.TodayNY())
  GROUP BY APP.external_id, dbo.ProperCase(exp.paid_to),exp.amount
  )
  select c.ASSET_ID
  ,#tmp.FULL_NAME [Property Owner(s)]
  ,dbo.ProperCase(p.address) as [Homeowner Address]
  ,c.file_num as [File Number]
  ,expense1.appraisal_fee as [Appraisal Fee Amount]
  ,expense2.appraisal_fee as [Appraisal Fee Amount (2nd)]
  ,expense.amount as [Origination Fee]
  ,c.net_wire_amt as [Total Wire Amount]
  FROM vClosingEx c
  JOIN vPipeline p on p.asset_id=c.asset_id
  JOIN #tmp on c.asset_id=convert(varchar(50),#tmp.EXTERNAL_ID)
  LEFT JOIN expenses as expense1 on c.asset_id=convert(varchar(50),expense1.EXTERNAL_ID) and expense1.RowNumber=1
  LEFT JOIN expenses as expense2 on c.asset_id=convert(varchar(50),expense2.EXTERNAL_ID) and expense2.RowNumber=2
  LEFT JOIN API_EXPENSE expense ON (convert(bigint,p.application_id) = expense.application_id and expense."TYPE" ='origination_charge')
  JOIN WSFS_Fundings f on c.asset_id = f.Asset_id 
  WHERE f.ValueDate=dbo.TodayNY();
  
  drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\BuyBack_DoNotSell.sql ---
select a.max_id
, a.full_name
, a.address_full
, a.investment_payment [investment_payment_$]
, a.effective_date
, a.uw_issue
, d.headline
,case when c.asset_id is null then '' else 'x' end [available_for_sale]
from vAssetsEx a
left join vAvailableCollateral c on c.asset_id=a.asset_id
left join vDefaultsEx d on d.asset_id = a.asset_id
where uw_issue is not null and final_disposition_date is null and a.uw_issue_include_in_reporting_flag=1
order by uw_issue,effective_date


--- FILE: ReportRunner\ReportRunner\SQL\ClearEdgeCollateral.sql ---
drop table if exists #tmp

select
  a.asset_id
  , a.effective_date
  , c.file_num
  , a.name_simple
  , a.address_full
  , accts.name [owner]
  , v.[name] [doc_custodian]
  , a.final_disposition_date
 
  into #tmp
  from 
    vPositionsLastOwner p
    join vAssetsEx a on a.asset_id = p.asset_id
    join vClosing c on p.asset_id = c.asset_id
    join vAccountsEx accts on accts.account_id = p.account_id
    join vVendors v on v.vendor_id = accts.doccustodian_id
   
 
  
    
  order by
    a.effective_date desc
    
   
    select asset_id,effective_date,file_num,name_simple,owner,doc_custodian from #tmp where (final_disposition_date is null)  order by effective_date desc
    select asset_id,effective_date,final_disposition_date,file_num,name_simple,owner,doc_custodian from #tmp where (final_disposition_date is not null) order by final_disposition_date desc
    
    drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\closing_table_investment_payment_check.sql ---
select (case when c.effective_date <> p.estimated_signing  then 'Signing Date Has Changed' else '' end) as 'Signing Date'
	, (case when c.investment_payment <> p.investment_payment then 'Investment Payment Has Changed' else '' end) as 'Investment Payment Pipeline'
	, (case when c.investment_payment <> o.INVESTMENT_AMOUNT then 'Investment Payment Has Changed' else '' end) as 'Investment Payment Offer'
	, c.asset_id
	, p.APPLICATION_STATE
	, c.customer_pipeline_label
	, c.effective_date as 'Closing Effective Date'
	, p.estimated_signing as 'Pipeline Estimated Sign'
	, c.investment_payment as 'Closing Inv Pmt'
	, p.investment_payment as 'Pipeline Inv Pmt' 
	, o.INVESTMENT_AMOUNT as 'Offer Inv Amt' 
	, o.INPUT_REQUESTED_OFFER as 'Offer Requested Amt' 
from vClosing c 
left join vPipeline p on p.asset_id = c.asset_id 
left join API_OFFER o on p.application_id = o.APPLICATION_ID
where c.asset_id not in (select id from Assets) 
and (c.effective_date <> p.estimated_signing  or c.investment_payment <> p.investment_payment or c.investment_payment <> o.INVESTMENT_AMOUNT or c.investment_payment <> o.INPUT_REQUESTED_OFFER) 
and c.effective_date > DATEADD(WEEK,-8,dbo.TodayNY()) order by c.effective_date desc


--- FILE: ReportRunner\ReportRunner\SQL\Closing_Table_Update_Effective_Dates.sql ---
DROP TABLE IF EXISTS #TMP

declare @v_asset_id asset_id_type, @v_Current_effective_date date, @v_max_estimated_close_on date, @v_count int

select c.asset_id as asset_id, c.effective_date as effective_date_closing_table, convert(date,app.ESTIMATED_CLOSE_ON) as max_estimated_close_on, 
convert(varchar(255),'') as status
into #tmp
from vClosing c 
left join api_application app on app.EXTERNAL_ID= c.asset_id 
where c.asset_id not in (select id from Assets) 
and c.effective_date <> app.ESTIMATED_CLOSE_ON
and c.effective_date > DATEADD(WEEK,-6,dbo.TodayNY())

declare estimated_signing_update_cursor cursor for 
select asset_id, effective_date_closing_table, max_estimated_close_on from #tmp

OPEN estimated_signing_update_cursor

FETCH NEXT FROM estimated_signing_update_cursor INTO @v_asset_id, @v_Current_effective_date , @v_max_estimated_close_on 
WHILE @@FETCH_STATUS = 0  
	BEGIN  
	
	select @v_count = isnull(count(*),0) from assets where id = @v_asset_id
	if @v_count = 0
		begin
		update Closing set EFFECTIVE_DATE = @v_max_estimated_close_on where asset_id = @v_asset_id
		update #tmp set status = concat('Closing Table Effective Date Has Been Updated:  From ' ,convert(varchar(10),convert(date,@v_Current_effective_date,101)) ,' to ' , convert(varchar(10),convert(date,@v_max_estimated_close_on,101)))
		where asset_id = @v_asset_id
		end
	FETCH NEXT FROM estimated_signing_update_cursor INTO @v_asset_id, @v_Current_effective_date , @v_max_estimated_close_on 
	END

CLOSE estimated_signing_update_cursor 
DEALLOCATE estimated_signing_update_cursor 


select * from #tmp
DROP TABLE IF EXISTS #TMP


--- FILE: ReportRunner\ReportRunner\SQL\Closing_Table_Update_Investment_Payment_issues.sql ---
select 
	(case when c.effective_date <> p.estimated_signing  then 'Signing Date Has Changed' else '' end) as 'Signing Date' 
	, (case when c.investment_payment <> p.investment_payment then 'Investment Payment Has Changed' else '' end) as 'Offer Investment Payment '
	, (case when c.investment_payment <> o.INVESTMENT_AMOUNT then 'Pipeline Investment Payment <> Offer Investment Payment ' else '' end) as 'Investment Payment'
	, c.asset_id, p.APPLICATION_STATE, c.customer_pipeline_label, c.effective_date as 'Closing Effective Date'
	, p.estimated_signing as 'Pipeline Estimated Sign', c.investment_payment as 'Closing Inv Pmt', p.investment_payment as 'Pipeline Inv Pmt' 
	from vClosing c 
	left join vPipeline p on convert(varchar(255),p.Max_id) = c.asset_id 
	left join api_offer o on o.APPLICATION_ID = p.application_id
	where c.asset_id not in (select id from Assets where added_to_badger < dbo.TodayNY()) 
		and (c.effective_date <> p.estimated_signing  or c.investment_payment <> p.investment_payment or c.investment_payment <> o.INVESTMENT_AMOUNT) 
		and c.effective_date > DATEADD(WEEK,-8,dbo.TodayNY()) order by c.effective_date desc


--- FILE: ReportRunner\ReportRunner\SQL\CollateralStatus.sql ---
exec dbo.DocStatus @summary=@summary, @detail=@detail, @days_heads_up=@days_heads_up, @accts=@accts


--- FILE: ReportRunner\ReportRunner\SQL\CollatLoadCompare.sql ---
declare @new int
declare @old int
declare @new_l smalldatetime
declare @old_l smalldatetime



select @new=max(load_id),@new_l=max(cl.file_create_date) from vCollatLoads cl where cl.account_id = account_id and cl.account_id = @account_id
select @old=max(load_id),@old_l=max(cl.file_create_date) from vCollatLoads cl where cl.account_id = account_id and cl.account_id = @account_id and load_id < @new





select @old_l [old_load], @new_l [new_load]

select

  a.asset_id
  , a.name_simple
  , a.address_simple
  , n.collateral_production_stage_code [cert_status]
  , dbo.BizDayDiff(cs.asof,n.report_time) [#_bdays]
  from 
    vCollatInv n 
  join 
    vAssetsEx a on n.asset_id = a.asset_id 
    left join vCollatInv o on o.load_id= @old and n.asset_id = o.asset_id
    left join vCollatShipmentsSingleEx cs on cs.collatshiptype_id = 1 and cs.asset_id = a.asset_id
    where 
      n.load_id= @new
      and o.asset_id is null
      order by dbo.BizDayDiff(cs.asof,n.report_time) DESC


select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , o.cert_status [cert_status_old]
  , n.cert_status [cert_status_new]
  
  from 
    vCollatInv n 
  join 
    vAssetsEx a on n.asset_id = a.asset_id 
    left join vCollatInv o on o.load_id= @old and n.asset_id = o.asset_id
    
    where 
      n.load_id= @new
      and n.cert_status != o.cert_status



select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , new.cert_status
  , new.doc_issue
  , new.days_since_sold
  , new.exception_sak [new_exception_sak]
  , old.exception_sak [old_exception_sak]
  from 
    vCollatExcEx new
  join 
    vAssetsEx a on new.asset_id = a.asset_id 
    left join vCollatExcEx old on old.collatload_id= @old and old.exception_sak = new.exception_sak
    where 
      new.collatload_id= @new
      and new.exception_sak is not null
      and old.exception_sak is null
    order by
      new.days_since_sold desc, a.name_simple
      
      
select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , old.cert_status [old_cert_status]
  , old.doc_issue [old_doc_issue]

  
  from 
    vCollatExcEx old
  join 
    vAssetsEx a on old.asset_id = a.asset_id 
    left join vCollatExcEx new on new.collatload_id= @new and old.exception_sak = new.exception_sak
    
    where 
      old.collatload_id= @old
      and new.exception_sak is null
      and old.exception_sak is not null
    order by name_simple


select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , o.[owner] [owner_old]
  , n.[owner] [owner_new]

  from 
    vCollatInvEx n 
  join 
    vAssetsEx a on n.asset_id = a.asset_id 
    left join vCollatInvEx o on o.load_id= @old and n.asset_id = o.asset_id
    where 
      n.load_id= @new
      and n.[owner] != o.[owner]


--- FILE: ReportRunner\ReportRunner\SQL\CollatNeedToTransfer.sql ---
select
  p.asset_id
  , p.account [investor]
  , c.borrower_name [name]
  , c.owner [doc_custodian_account]
  , p.last_settle
  , datediff(d,p.last_settle,dbo.TodayNY()) [days_since_settle] 
  , last_trade_id
  into #tmp
  from
  vPositions p
  left join vCollatInvEx C on p.asset_id = C.asset_id and latest = 1 where
  p.account_id != 1
  and p.account_id != C.account_id
  and datediff(d,p.last_settle,dbo.TodayNY()) > 3
  and p.account_id not in (4)

 
  
  
  select count(*) [#],last_settle,investor, doc_custodian_account, last_trade_id from #tmp group by investor, doc_custodian_account, last_trade_id,last_settle ORDER BY last_settle ASC
select * from #tmp

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\CustomerPipeline.sql ---
exec dbo.GetClosingPipeline @account_id=@account_id


--- FILE: ReportRunner\ReportRunner\SQL\DailyAvailableToTrade.sql ---
drop table if exists #tmpFunding
drop table if exists #tmpFundingPivot
drop table if exists #tmpFundingSummary

select 
  b.nice_name [funded account],
  ac.*, 
  n.funding_status [unlock_funding_status], 
  n.value_date, 
  case 
    when ac.WSFS_Certification_Status = 'Certified' and ac.funds_disbursed_by_title_company = 1 then 'TRUE'
    else 'FALSE'
    end [available to trade]
into #tmpFunding
from dbo.vAvailableCollateral ac
  left outer join dbo.vFundings_New n on ac.asset_id = n.asset_id and n.funding_status != 'Cancelled' and n.funding_type = 'Deal'
  left outer join dbo.BankAccts b on b.id = n.bankacct_id
order by [available to trade] desc, ac.effective_date asc

select 
    format(getdate(),'MM/dd/yyy') [Date]
    , count(*) [# Balance Sheet]
    ,format(sum(t.investment_payment),'c','en-US') [$ Balance Sheet ]
    , sum(case when [available to trade] = 'TRUE' THEN 1 ELSE 0 END) [# Tradeable]
    ,format(sum(case when [available to trade] = 'TRUE' THEN t.investment_payment ELSE 0 END),'c','en-US') [$ Tradeable]
    , sum(case when [available to trade] = 'TRUE' THEN 0 ELSE 1 END) [# Not Yet Tradeable]
    ,format(sum(case when [available to trade] = 'TRUE' THEN 0 ELSE t.investment_payment  END),'c','en-US') [$ Not Yet Tradeable]
 
    into #tmpFundingSummary
from #tmpFunding t



select 
    4 [order]
    ,convert(varchar(50),'Total') [Asset Status]    
    ,count(*) [#]
    ,format(sum(t.investment_payment),'c','en-US') [$]
into #tmpFundingPivot
from #tmpFunding t



insert into #tmpFundingPivot
select 
    0 [order]
    ,'Tradeable' [Asset Status]  
    ,sum(case when [available to trade] = 'TRUE' THEN 1 ELSE 0 END) [Count]
    ,format(sum(case when [available to trade] = 'TRUE' THEN t.investment_payment ELSE 0 END),'c','en-US') [$]
from #tmpFunding t



insert into #tmpFundingPivot
select 
    1
    ,'Certified, not Funded'
    ,sum(case when t.WSFS_Certification_Status = 'Certified' and t.funds_disbursed_by_title_company = 0 then 1 else 0 end) [#]
    ,format(sum(case when t.WSFS_Certification_Status = 'Certified' and t.funds_disbursed_by_title_company = 0 then t.investment_payment else 0 end),'c','en-US') [$]
from #tmpFunding t



insert into #tmpFundingPivot
select 
    2,
    'Funded, not Certified'
    ,sum(case when t.WSFS_Certification_Status <> 'Certified' and t.funds_disbursed_by_title_company = 1 then 1 else 0 end) [#]
    ,format(sum(case when t.WSFS_Certification_Status <> 'Certified' and t.funds_disbursed_by_title_company = 1 then t.investment_payment else 0 end),'c','en-US') [$]
 from #tmpFunding t



insert into #tmpFundingPivot
select 
    3,
    'Not Certified or Funded'
    ,sum(case when t.WSFS_Certification_Status <> 'Certified' and t.funds_disbursed_by_title_company = 0 then 1 else 0 end) [#]
    ,format(sum(case when t.WSFS_Certification_Status <> 'Certified' and t.funds_disbursed_by_title_company = 0 then t.investment_payment else 0 end),'c','en-US') [$]
from #tmpFunding t





select CONCAT('[', t.date, '] Balance Sheet Asset Summary ', char(10), char(149), ' Tradeable:   ',t.[$ Tradeable], char(10), char(149) , ' Pending:     ',  t.[$ Not Yet Tradeable]) 
from #tmpFundingSummary t


select *
from #tmpFundingSummary t

select [Asset Status],[#],[$] from #tmpFundingPivot order by [order]

select * from #tmpFunding







drop table if exists #tmpFunding
drop table if exists #tmpFundingPivot
drop table if exists #tmpFundingSummary


--- FILE: ReportRunner\ReportRunner\SQL\DailyBalanceSheetAssets.sql ---
BEGIN 

DECLARE @cutoff as date
DECLARE @orig_cutoff as date

SET @cutoff = (convert(varchar(10),getdate(),101))   

SELECT @orig_cutoff = g.[value] FROM Globals g WHERE g.[key] = 'CUTOFF'


UPDATE Globals SET [value] = CONVERT(varchar,@cutoff,101) WHERE [key] = 'CUTOFF'


DROP table IF exists #tmpT





SELECT t.*
INTO #tmpT
FROM (


  SELECT p.account
  , null as [trade_date]
  
  , null as [settle_date]  
  , null as [trade_id]
  , p.investment_payment
  , a.asset_id
  , a.max_id
  , a.effective_date  
  , a.address_simple
  , a.city
  , a.zip
  , a.state
  , a.investment_pct
  , a.cost_limit
  , a.exchange_rate
  , a.property_type
  , a.exercise_value_cutoff [exercise value]
  , case when p.account in ('UPS BUYBACK') then p.last_trade else null end  repurchase_date
  , case when p.account in ('UPS BUYBACK') then p.wavg_px else null end  repurchase_price
  , p.account [status]
    FROM dbo.vPositions p
    JOIN dbo.vAssetsExCutoff a on p.asset_id = a.asset_id
     LEFT JOIN dbo.vFundings_New n on a.asset_id = n.asset_id and n.funding_status != 'Cancelled' and n.funding_type = 'Deal'
     LEFT JOIN dbo.FundingStatus s on n.fundingstatus_id = s.id
     

   
  WHERE (p.account in ('UPS BUYBACK','UPS')                        
  or (p.account in ('UFT1','UF2') AND n.amount is not null))       
    and a.final_disposition_date is null


UNION

  
  
  


  SELECT p.account
  , t.trade_date
  , t.settle_date
  , t.trade_id
  , p.investment_payment
  , a.asset_id
  , a.max_id
  , a.effective_date    
  , a.address_simple
  , a.city
  , a.zip
  , a.state
  , a.investment_pct
  , a.cost_limit
  , a.exchange_rate
  , a.property_type
  , a.exercise_value_cutoff [exercise value]  
  , case when p.account in ('UPS BUYBACK') then p.last_trade else null end  repurchase_date
  , case when p.account in ('UPS BUYBACK') then p.wavg_px else null end  repurchase_price
  , 'Traded (unsettled)' [status]
   FROM dbo.vPositions p
    JOIN dbo.vTradesEx t on p.asset_id = t.asset_id and t.is_settled = 0 and t.is_journal = 0 and t.is_unlock = 0
    JOIN dbo.vAssetsExCutoff a on p.asset_id = a.asset_id
    LEFT JOIN dbo.Buybacks b on a.asset_id = b.asset_id

   
  WHERE a.final_disposition_date IS null
) t






/* 
SELECT [status], count(*) [# assets], format(sum(t.investment_payment),'N0') [$ inv pmt]
FROM #tmpT  t
group by [status]
union 
SELECT 'Total' [status], count(*) [# assets], format(sum(t.investment_payment),'N0') [$ inv pmt]
FROM #tmpT  t
ORDER BY [# assets]

/* 
SELECT * FROM #tmpT order by settle_date desc, account

DROP table IF exists #tmpT


UPDATE Globals SET [value] = CONVERT(varchar,@orig_cutoff,101) WHERE [key] = 'CUTOFF'
  
COMMIT TRANSACTION


--- FILE: ReportRunner\ReportRunner\SQL\DailyFirstAmericanBreakdown.sql ---
DECLARE @value_date DATE = dbo.TodayNY();

WITH first_american_wires AS (
    SELECT SUBSTRING(DescText, 1, 14) AS fa_asset_id,
        tcbinv_id AS banktrans_id,
        AsOfDate AS wire_date,
        CreditAmt
    FROM 
        vTCBInvEx
    WHERE 
        AcctNo = 2400101364
        AND DescText LIKE '%First American%'
        AND AsOfDate = @value_date
),
appraisal_fee AS (
    SELECT 
        app.external_id AS asset_id,
        exp.amount AS appraisal_fee,
        ROW_NUMBER() OVER (PARTITION BY app.external_id ORDER BY exp.MODIFIED_AT DESC) AS row_number
    FROM 
        API_APPLICATION app
        LEFT JOIN API_APPLICATIONPROFILE app_pro ON app.ID = app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL 
        LEFT JOIN API_PROFILE pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
        LEFT JOIN API_EXPENSE exp ON exp.APPLICATION_ID = app.ID AND exp.DELETED_AT IS NULL
    WHERE 
        exp.name LIKE 'Appraisal%' 
),
concessions AS (
    SELECT 
        app.external_id AS asset_id,
        exp.amount AS concessions,
        ROW_NUMBER() OVER (PARTITION BY app.external_id ORDER BY exp.MODIFIED_AT DESC) AS row_number
    FROM 
        API_APPLICATION app
        LEFT JOIN API_APPLICATIONPROFILE app_pro ON app.ID = app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL 
        LEFT JOIN API_PROFILE pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
        LEFT JOIN API_EXPENSE exp ON exp.APPLICATION_ID = app.ID AND exp.DELETED_AT IS NULL
    WHERE 
        exp.name LIKE 'Concession%'
)

SELECT 
    fa.fa_asset_id,
    c.file_num,
    FORMAT(fa.wire_date, 'M/d/yyyy') AS wire_date,
    fa.CreditAmt AS wire_amount_$,
    ROUND(ISNULL(c.origination_fee, 0), 2) AS origination_fee_$,
    ROUND(ISNULL(a.appraisal_fee, 0), 2) AS appraisal_fee_$,
    ROUND(ISNULL(con.concessions, 0), 2) AS concessions_$,   
    ROUND(
        fa.CreditAmt 
        - ISNULL(c.origination_fee, 0) 
        - ISNULL(a.appraisal_fee, 0) 
        + ISNULL(con.concessions, 0), 
    2) AS net_amount_$
FROM 
    first_american_wires fa
JOIN 
    vClosingEx c ON fa.fa_asset_id = c.asset_id
LEFT JOIN 
    appraisal_fee a ON a.asset_id = c.asset_id AND a.row_number = 1
LEFT JOIN 
    concessions con ON con.asset_id = c.asset_id AND con.row_number = 1
ORDER BY 
    fa.wire_date, fa.fa_asset_id;


--- FILE: ReportRunner\ReportRunner\SQL\DailyFundedVsJournaled.sql ---
SELECT 
	f.asset_id, 
	f.value_date,
	f.amount,
	f.nice_name, 
	f.funding_status
FROM vFundings_New f
   LEFT JOIN vTradesEx t on t.asset_id = f.asset_id
WHERE f.funding_status != 'Cancelled' and f.funding_type = 'Deal'
and t.asset_id is null











select
	t.asset_id,
	t.trade_date,
	t.settle_date,
	t.name_simple,
	t.account,
	t.investment_payment,
	t.ticket_id,
	t.trade_id
FROM vTradesEx t
   LEFT JOIN vFundings_New f on t.asset_id = f.asset_id
WHERE f.funding_status != 'Cancelled' and f.funding_type = 'Deal'
and f.asset_id is null


--- FILE: ReportRunner\ReportRunner\SQL\DailyPrepay.sql ---
declare @last_month_outstanding float
declare @payoffs_this_month float
declare @payoffs_this_month_count int
declare @last_month_date date
declare @last_month_outstanding_count int



declare @days_360 int
declare @cutoff date



drop table if exists #outstanding
drop table if exists #payoffs
drop table if exists #a
drop table if exists #last_month
drop table if exists #payoffs_accts

select @cutoff = dateadd(d,-1,dbo.GetDateNY())
select @last_month_date = eomonth(@cutoff,-1)


select * into #a from vAssets where effective_date <= dateadd(m,-@age_filter_months,@cutoff) or @age_filter_months is null

select count(*) [#], p.account, sum(a.investment_payment) [outstanding_prior_me],convert(float,0) [payoff_this_month],convert(float,0) [no_more_payoffs_CPR], convert(float,null) [mtd_cpr],convert(int,null) [payoff_count] into #last_month from #a a left join vPositions p on p.asset_id = a.asset_id where effective_date <= @last_month_date and (a.final_disposition_date is null or a.final_disposition_date > @last_month_date) group by p.account
select count(*) [payoff_count],p.account, sum(a.investment_payment) [payoffs] into #payoffs_accts from #a a left join vPositions p on p.asset_id = a.asset_id where (final_disposition_date > @last_month_date and a.final_disposition_date <= @cutoff) group by p.account

update lm set [payoff_this_month] = p.payoffs,payoff_count=p.payoff_count  from #last_month lm join #payoffs_accts p on p.account = lm.account
update lm set [no_more_payoffs_CPR] = (1-power(1-([payoff_this_month]/outstanding_prior_me),12))*100.0  from #last_month lm
update lm set [mtd_cpr] = (1-power(1-([payoff_this_month]/outstanding_prior_me),360.0/datepart(day,@cutoff)))*100.0  from #last_month lm


select @last_month_outstanding=sum([outstanding_prior_me]),@last_month_outstanding_count=sum(#) from #last_month
select @payoffs_this_month_count=sum(payoff_count),@payoffs_this_month =  sum(payoffs) from #payoffs_accts







select 
  d.date
  , sum(investment_payment) [payoffs_30]
  , count(*) [payoffs_cnt] 
  , dateadd(d,-30,d.date) [30_day_back_date]
  into #payoffs
  from 
  Dates d
  left join (select final_disposition_date,sum(investment_payment) [investment_payment] from #a group by final_disposition_date) a on a.final_disposition_date > dateadd(d,-30,d.date) and a.final_disposition_date <= d.date
  
  where 
   d.date <= @cutoff
   

  group by d.date
  order by d.date desc
  

select 
  d.date
  , sum(investment_payment) [outstanding]
  , count(*) [outstanding_cnt]
  into #outstanding
  from 
  Dates d
 
  left join (select effective_date,final_disposition_date,sum(investment_payment) [investment_payment] from #a group by effective_date,final_disposition_date) a on a.effective_date <= d.date and (a.final_disposition_date is null or a.final_disposition_date > d.date) 
  
  where 
  d.date <= @cutoff
 
  group by d.date
  order by d.date asc


select 
  @last_month_outstanding_count [outstanding_prior_me_#]
  , @last_month_outstanding [outstanding_prior_me_$]
  , @payoffs_this_month_count [payoff_this_month_#]
  , @payoffs_this_month [payoff_this_month_$]
  , (1-power(1-(@payoffs_this_month/@last_month_outstanding),12))*100.0 [no_more_payoffs_CPR_|0.00|]
  , (1-power(1-(@payoffs_this_month/@last_month_outstanding),360.0/datepart(day,@cutoff)))*100.0 [MTD_CPR_|0.00|]



 select 
  [account]
  , [#]  [outstanding_prior_me_#]
  , outstanding_prior_me [outstanding_prior_me_$]
  , [payoff_count] [payoff_this_month_#]
  , payoff_this_month [payoff_this_month_$]
  , no_more_payoffs_CPR [no_more_payoffs_CPR_|0.00|]
  , mtd_cpr [MTD_CPR_|0.00|]
  from 
    #last_month order by outstanding_prior_me desc
    


select
 d.date
 
 , o.outstanding_cnt [outstanding_inv_pmt_30_back_#]
 , o.outstanding [outstanding_inv_pmt_30_back_$]
 , p.payoffs_30 [payoffs_last_30_$]
 , p.payoffs_cnt [payoff_count_last_30]
 , (1-power(1-(p.payoffs_30/o.outstanding),12))*100.0 [rolling_30_day_CPR_|0.00|]
 from
  Dates d
  left join #outstanding o on o.date = dateadd(d,-30,d.date)
  left join #payoffs p on p.date = d.date
 where
 
  d.date >= dateadd(d,-30,@cutoff) and d.date <= @cutoff
 order by d.date desc
    
    drop table if exists #outstanding
    drop table if exists #payoffs
    drop table if exists #a
    drop table if exists #last_month
    drop table if exists #payoffs_accts


--- FILE: ReportRunner\ReportRunner\SQL\DailyTradeImport.sql ---
DROP table IF exists #tmp
  
	
	SELECT APP.EXTERNAL_ID, STRING_AGG(concat(FIRST_NAME, ' ',LAST_NAME), ' & ') [FULL_NAME]
	INTO #tmp FROM API_APPLICATION APP
	LEFT JOIN api_applicationprofile app_pro ON app.ID =app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL AND app_pro._FIVETRAN_DELETED = 0
	LEFT JOIN api_profile pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
	WHERE convert(varchar(50),app.EXTERNAL_ID) IN (SELECT asset_id FROM Fundings_New WHERE fundingstatus_id=3 and value_date=dbo.TodayNY())
	GROUP BY APP.EXTERNAL_ID;

  
  WITH expenses as
  (  
  SELECT APP.external_id,CASE WHEN dbo.ProperCase(exp.paid_to)='Accurategroup' THEN 'Accurate Group' ELSE dbo.ProperCase(exp.paid_to) END AS [appraisal_vendor],exp.amount [appraisal_fee],ROW_NUMBER() OVER(PARTITION BY APP.external_id ORDER BY exp.amount) AS RowNumber
  FROM API_APPLICATION APP
	LEFT JOIN api_applicationprofile app_pro ON app.ID =app_pro.APPLICATION_ID AND app_pro.DELETED_AT IS NULL AND app_pro._FIVETRAN_DELETED = 0
	LEFT JOIN api_profile pro ON app_pro.PROFILE_ID = pro.ID AND pro.DELETED_AT IS NULL
  LEFT JOIN API_EXPENSE exp on exp.application_id = app.id AND exp.DELETED_AT IS NULL
	WHERE exp.name like 'Appraisal%' and convert(varchar(50),app.EXTERNAL_ID) IN (SELECT asset_id FROM Fundings_New WHERE fundingstatus_id=3 and value_date=dbo.TodayNY())
  GROUP BY APP.external_id, dbo.ProperCase(exp.paid_to),exp.amount
  )
  SELECT
  'Trade' as [Record Type (Trade / Fee)]  
  ,'New' as [Upload Mode (New / Update / Void)]
  ,NULL as [Prime Broker Account ID]
  ,'Unlock Technologies, Inc.' as [Portfolio (Mandatory for Trade)]
  ,'Unlock Partnership Solutions Inc (Main)' as [Designated Account (Mandatory for Trade)]
  ,'UNLUPS00_First Republic (80009175797)' as [Custodian Account (Mandatory for Trade)]
  ,'First Republic Bank' as [Custodian (Mandatory for Trade)]
  ,NULL as [Trade Reference (Mandatory for Trade / Fee)]
  ,dbo.TodayNY() as [Trade Date (Mandatory for Trade)]
  ,dbo.TodayNY() as [Settlement Date (Mandatory for Trade)]
  ,NULL as [Trader]
  ,NULL as [Strategy]
  ,NULL as [Sub Strategy]
  ,'Do Not Send' as [Send To Prime Broker (Send / Do Not Send / Yes / No)]
  ,NULL as [Comments]
  ,'B' as [Buy Sell (B-Buy/S-Sell/BC-Buy Cover/SS-Sell Short) (Mandatory for Trade)]
  ,c.INVESTMENT_PAYMENT as [Quantity (Mandatory for Trade)]
  ,1 as [Price (Mandatory for Trade)]
  ,NULL as [Clearing Mode]
  ,'ClearEdge Title, Inc' as [Counter Party Dealer (Mandatory for Trade)]
  ,'USD' as [Trade Currency (Mandatory for New Security)]
  ,'P' as [Settle Currency Ind (P-Portfolio /L-Local / O-Other)]  
  ,'USD' as [Settle Currency Type]
  ,NULL as [Currency Exchange FXRate]
  ,'Equity' as [Asset Class (Mandatory for New Security)]
  ,dbo.ProperCase(CONCAT(p.address, ' (',#tmp.FULL_NAME,')')) as [Security Name]
  ,'Other' as [Security Reference Type (Mandatory for New Security)]
  ,c.ASSET_ID as [Security Reference (Mandatory for Trade)]
  ,'United States' as [Exchange (Mandatory for New Security)]
  ,NULL as [Sector]
  ,NULL as [Sub Sector]
  ,NULL as [Fee Type (Mandatory for Fee)]
  ,NULL as [Amount (Mandatory for Fee)]
  ,NULL as [Currency Type Code (Mandatory for Fee)]
  ,NULL as [Fee FX Rate]
  ,NULL as [Security Reference Type 2]
  ,NULL as [Security Reference 2]
  ,NULL as [Execution Platform]
  ,NULL as [Custom Tag (e.g. CustomGroup1: CustomTag1, CustomTag2; CustomGroup2: CustomTag3)]
  ,NULL as [BBGYellow Key]
  ,NULL as [Trade Journal YN]
  ,NULL as [Journal Category]
  ,NULL as [Include In Settlement (1 - Yes, 0 - No)]
  ,NULL as [Execution Methodology (e.g. EM1; EM2)]
  ,NULL as [Send To Fund Administrator (Send / Do Not Send / Yes / No)]
  ,NULL as [Override Cost Date]
  ,dbo.ProperCase(p.address) as [Homeowner Address]
  ,expense1.appraisal_vendor as [Appraisal Vendor]
  ,expense1.appraisal_fee as [Appraisal Fee Amount]
  ,expense2.appraisal_vendor as [Appraisal Vendor (2nd)]
  ,expense2.appraisal_fee as [Appraisal Fee Amount (2nd)]
  ,expense.amount as [Origination Fee]
  ,c.net_wire_amt as [Total Wire Amount]
  ,c.file_num as [File Number]
  ,#tmp.FULL_NAME as [Property Owner(s)]
  ,ref.description as [Referral Partner]
  ,CASE WHEN c.commission_amount=0 THEN null ELSE c.commission_amount END as [Commission Amount]
  ,f.nice_name as [Funding Account]
  FROM vClosingEx c
  JOIN vPipeline p on p.asset_id=c.asset_id
  JOIN vFundings_New f on f.asset_id=c.asset_id
  JOIN #tmp on c.asset_id=convert(varchar(50),#tmp.EXTERNAL_ID)
  LEFT JOIN expenses as expense1 on c.asset_id=convert(varchar(50),expense1.EXTERNAL_ID) and expense1.RowNumber=1
  LEFT JOIN expenses as expense2 on c.asset_id=convert(varchar(50),expense2.EXTERNAL_ID) and expense2.RowNumber=2
  LEFT JOIN API_EXPENSE expense on (convert(bigint,p.application_id) = expense.application_id and expense."TYPE" ='origination_charge')
  LEFT JOIN ReferralCommissionInfo ref on c.referral_email = ref.email_full
  WHERE f.fundingstatus_id=3 and f.value_date=dbo.TodayNY()
  
  SELECT transaction_date,amount,[description],REPLACE(REPLACE(RIGHT(supplementary_details, LEN(supplementary_details) - CHARINDEX('REMARK=', supplementary_details) - 2),'=',' '),' PH:727-339-6562; ','')[OBI]
  FROM BankActivity 
  WHERE transaction_type_id in (2,3)
  and account_id=1309823
  and transaction_date=dbo.TodayNY()
  ORDER BY transaction_date
  
  DROP table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\DansDay.sql ---
declare @mouse_thresh int = 30
declare @begin date
declare @end date
declare @hours int
declare @hours_calc float

select @begin = dbo.TodayNY()
select @end = @begin


drop table if exists #t

select *,convert(varchar(80),null) [category] into #t from WindowWatcher w WHERE LAST_MOUSE_MOVE < @mouse_thresh and cast(update_time as date) between @begin and @end

update t set [category] = 'Email' from #t t where t.active_exe = 'OUTLOOK'
update t set [category] = 'Bloomberg' from #t t where t.active_exe = 'bplus.wtk2'


update t set [category] = 'HouseMoney' from #t t where t.window_title like '%HouseMoney%'
update t set [category] = 'HouseMoney' from #t t where t.window_title like '%Hawaii%'
update t set [category] = 'HouseMoney' from #t t where t.window_title like '%Rippling%'
update t set [category] = 'HouseMoney' from #t t where t.window_title like '%Pitkin%'


update t set [category] = 'HR/PAYROLL' from #t t where category is null AND (t.window_title like '%trinet%' OR t.window_title like 'trinet%')

update t set [category] = 'Zoom' from #t t where category is null AND t.active_exe = 'zoom'

update t set [category] = 'Trade Ticketing' from #t t where category is null AND t.window_title like 'Forward Sale Data Schedule%'

update t set [category] = 'Reporting/Cash Money' from #t t where category is null AND t.window_title like 'Cash Money%'
update t set [category] = 'Reporting/Quality Checklist' from #t t where category is null AND t.window_title like 'Quality Checklist.xlsb%'
update t set [category] = 'Reporting/Cap Table' from #t t where category is null AND t.window_title like 'Cap Calcs.xlsx%'
update t set [category] = 'Reporting/Cap Table' from #t t where category is null AND active_exe = 'excel' and t.window_title like '00 - File Worksheet -%'

update t set [category] = 'Company Admin/Main Spreadsheet' from #t t where category is null AND t.window_title like 'Important.xl%'
update t set [category] = 'Company Admin/Legal & Registrations' from #t t where category is null AND t.window_title like '%northwestregisteredagent%'
update t set [category] = 'Post Closing/Printing Label' from #t t where category is null AND t.active_exe = 'DYMOConnect'
update t set [category] = 'Post Closing/Document Custodian' from #t t where category is null AND t.active_exe = 'chrome' and t.window_title like 'U.S. Bank Trust%'

update t set [category] = 'Coding/Database' from #t t where category is null AND t.active_exe = 'toad'
update t set [category] = 'Coding/Badger' from #t t where category is null and t.active_exe = 'devenv' and t.window_title like 'Badger%- %'
update t set [category] = 'Coding/ReportRunner' from #t t where category is null and t.active_exe = 'devenv' and t.window_title like 'ReportRunner%- %'
update t set [category] = 'Coding/Window Watcher' from #t t where category is null and t.active_exe = 'devenv' and t.window_title like 'Window Watcher%- %'
update t set [category] = 'Coding/Unlock Toolkit' from #t t where category is null and t.active_exe = 'devenv' and t.window_title like 'Unlock Toolkit%- %'
update t set [category] = 'Coding/UNKNOWN' from #t t where category is null and T.WINDOW_TITLE is null and t.active_exe = 'devenv'

update t set [category] = 'Badger Infrastructure Mtmgt/Database' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%UAM (unlock/UAM)%Microsoft Azure%' 
update t set [category] = 'Badger Infrastructure Mtmgt/Virtual Machine' from #t t where category is null and t.window_title like '%- Remote Desktop Connection'
update t set [category] = 'Badger Infrastructure Mtmgt/AZURE' from #t t where category is null and t.window_title like '%azure%'

update t set [category] = 'Badger' from #t t where category is null and t.active_exe = 'badger'

update t set [category] = 'Monday/UAM Calendar' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%UAM Cal - %'
update t set [category] = 'Monday/State Rollout' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%State Rollout - %'
update t set [category] = 'Monday/UAM Support' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%UAM Support - %'
update t set [category] = 'Monday/LFG' from #t t where category is null and t.active_exe = 'chrome' and t.window_title like '%LFG%- %Google Chrome'
update t set [category] = 'Monday/Lien Alert' from #t t where category is null and t.active_exe = 'chrome' and t.window_title like '%UAM Lien Alert%-%Google Chrome'
update t set [category] = 'Monday/Customer Pipeline' from #t t where category is null and t.active_exe = 'chrome' and t.window_title like '%Customer Pipeline%-%Google Chrome'

update t set [category] = 'Treasury' from #t t where category is null and t.active_exe = 'chrome' and t.window_title like '%First Republic Bank%'
update t set [category] = 'Treasury' from #t t where category is null and t.active_exe = 'chrome' and t.window_title like '%BREX%'

update t set [category] = 'Physical Mail' from #t t where category is null and t.active_exe = 'chrome' and (t.window_title like '%Earth Class Mail%' OR t.window_title LIKE '%Inbox Pieces%')


update t set [category] = 'Personal/Spotify' from #t t where category is null and  t.active_exe = 'spotify'
update t set [category] = 'Personal/Gmail' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%nitecow@gmail.com%' 
update t set [category] = 'Personal/GChat' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '% - Chat' 
update t set [category] = 'Personal/FB Messenger' from #t t where category is null and  t.active_exe = 'Messenger' and t.window_title = 'Messenger'
update t set [category] = 'Personal/FB Messenger' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like 'Messenger | Facebook%'
update t set [category] = 'Slack' from #t t where t.active_exe = 'slack' and category is null
update t set [category] = 'Teams' from #t t where t.active_exe = 'teams' and category is null

update t set [category] = 'FedEx' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like 'FedEx Ship Manager%' 
update t set [category] = 'DocuSign' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%DocuSign%' 
update t set [category] = 'DocSend' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%DocSend%' 
update t set [category] = 'LinkedIn' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like '%LinkedIn -%' 

update t set [category] = 'BAIRD' from #t t where category is null and t.window_title like '% - Desktop Viewer'

update t set [category] = 'DEALS/SLICK' from #t t where category is null and t.window_title like 'Slickdeals: %'
update t set [category] = 'DEALS/BENS' from #t t where category is null and t.window_title like 'Ben%s Bargains - %'
update t set [category] = 'DEALS/TECHBARGAINS' from #t t where category is null and t.window_title like 'Techbargains%'

update t set [category] = 'Web Browsing/Amazon' from #t t where category is null and  t.active_exe = 'chrome' and t.window_title like 'Amazon.com%'

update t set [category] = 'On Phone' from #t t where category is null and t.active_exe = 'RingCentral'

update t set [category] = 'UNDETECTABLE/Windows Explorer' from #t t where category is null and T.WINDOW_TITLE is null and t.active_exe = 'explorer'
update t set [category] = 'UNDETECTABLE/Chrome' from #t t where category is null and T.WINDOW_TITLE is null and t.active_exe = 'chrome'
update t set [category] = 'UNDETECTABLE/Chrome' from #t t where category is null and T.WINDOW_TITLE  = 'New Tab - Google Chrome' and t.active_exe = 'chrome'
update t set [category] = 'UNDETECTABLE/Chrome' from #t t where category is null and T.WINDOW_TITLE  = 'Google - Google Chrome' and t.active_exe = 'chrome'
update t set [category] = 'UNDETECTABLE/Visual Studio' from #t t where category is null and t.active_exe = 'devenv'




select @hours = sum(interval) from #t
select @hours_calc = datediff(mi,min(update_time),max(update_time))/60.0 from #t
select min(update_time) [clock_in], max(update_time) [clock_out],@hours_calc  [hours_|0.00|] from #t

select category,sum(interval)/60.0/60.0 [hours_|0.00|],sum(interval)/@hours_calc [%_|0.0%|] from #t group by category order by sum(interval) DESC
select active_exe,window_title,sum(interval)/60.0 [minutes_|0.0|] from #t t where category is null group by window_title,active_exe order by sum(interval) DESC



drop table #t


--- FILE: ReportRunner\ReportRunner\SQL\DaysInEscrow.sql ---
SELECT 
   c.asset_id,
   c.customer_pipeline_label,
   c.effective_date,
   f.value_date [funding_date],
   c.investment_payment [investment_payment_$],
   c.cet_days_in_escrow,
   c.cet_delay_reason 
FROM 
    vFundings_New f LEFT JOIN vClosingEx c on f.asset_id = c.asset_id 
WHERE 
    (f.fundingstatus_id=3 and f.fundingtype_id =1) and c.cet_days_in_escrow > 2 and c.funding_status <> 1
ORDER BY c.cet_days_in_escrow desc;

SELECT 
    c.asset_id,
    c.customer_pipeline_label,
    c.effective_date, 
    f.value_date [funding_date], 
    c.investment_payment [investment_payment_$], 
    DATEDIFF(DAY, f.value_date, dbo.TodayNY()) AS days_in_escrow,
    f.note
FROM 
    vFundings_New f LEFT JOIN vClosingEx c ON f.asset_id = c.asset_id
WHERE 
    f.asset_id NOT IN (SELECT fa_asset_id FROM FirstAmericanWireBreakdown) AND f.fundingstatus_id = 3 AND f.title_escrow_company = 'First American Title' and c.funding_status <> 1 
ORDER BY days_in_escrow desc;


--- FILE: ReportRunner\ReportRunner\SQL\DeceasedHomeowners.sql ---
drop table if exists #tmp

select 
  a.asset_id
  , a.name_simple
  , a.address_simple
  , a.effective_date
  , a.investment_payment [investment_payment_$]
  , min(csa.asOf) [first_detected]
  , min(case when a.applicant_partner_id is not null then 3 else case when a.dual_applicants=1 then 2 else 1 end end) [num_of_applicants]
  , case when a.effective_date > DATEADD(m,-6,dbo.TodayNY()) then 'RECENTLY ORIGINATED' else case when min(csa.asOf) > DATEADD(m,-1,dbo.TodayNY()) then 'RECENTLY DETECTED' end end [critical_note]
  into #tmp
  from
    vAssetsEx a
    join vCRAssetMap csa on csa.asset_id = a.asset_id
    left join CRScores cs on cs.creditfile_id = csa.creditfile_id
    left join CRScoreFactors csf on cs.id = csf.creditscore_id
    left join CRFactorCodes cf on csf.factorcode_id = cf.id
    
    
    
    left join vCRComments crc on crc.creditfile_id = csa.creditfile_id
  where
    a.final_disposition_date is null
    
    and (cf.factor_text like '%deceased' or crc.comment like '%deceased%' )
    
    and a.asset_id not in ('3420-545-1090-000/7','42713782664761') 
  group by
      a.asset_id
  , a.name_simple
  , a.address_simple
  , a.effective_date
  , a.investment_payment
  order by
    a.name_simple

  select distinct asset_id,name_simple,address_simple,effective_date,[investment_payment_$],[first_detected],[num_of_applicants],[critical_note] from #tmp order by first_detected asc
  
  select a.asset_id,ae.full_name,a.address_simple,a.effective_date from vAssetsEx a join vApplicantsEx ae on ae.asset_id = a.asset_id where ae.applicanttype_id=1 and ae.deceased=1 

  drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\DefaultLedger.sql ---
SELECT d.asset_id
, a.max_id
, a.last_name
, a.account
, a.investment_payment
, a.effective_date
, a.final_disposition_date [closing_date]
, d.default_date
, d.cure_date
, d.is_cured
, dt.[type] [default_type]
, dt.subtype [default_subtype]
, d.headline
, a.state
, s.judicial
, a.credit_score [orig_credit_score_|0|]
, a.credit_score_calc_current [curr_credit_score]
, a.lien_position [lien_pos]
, a.exchange_rate [exch_rate]
, a.cost_limit [ACL]
, a.ltv
, format(((a.secured_debt+a.investment_payment_current)*1.0)/(a.starting_home_value*1.0),'P') [CLTV]
, a.total_home_finance [THF_%]
, a.total_home_finance_limit [THFL_%]
, case when de.defaulteventtype_id=1 then de.[date] else null end [REF_TO_COUNSEL_ON]
, case when de.defaulteventtype_id=5 then de.[date] else null end [AUCTION_DATE]
, n.note [LATEST_NOTE]
FROM dbo.vDefaults d
JOIN dbo.vDefaultTypes dt on d.defaulttype_id = dt.defaulttype_id
JOIN dbo.vAssetsPositionEx a on d.asset_id = a.asset_id
JOIN dbo.States s on s.state = a.state
LEFT OUTER JOIN dbo.vDefaultEventsEx de on d.default_id = de.default_id
LEFT OUTER JOIN dbo.ForeignIDs fid ON fid.foreign_id = d.default_id and fid.asset_id = d.asset_id
LEFT OUTER JOIN dbo.vNotes AS n ON n.foreignid_id = fid.id AND n.latest_foreign = 1
ORDER BY d.default_date


--- FILE: ReportRunner\ReportRunner\SQL\DisposedAssetsAccounting.sql ---
declare @bom DATE

select @bom =DATEADD(day, -@days_back, dbo.TodayNY()) 

drop table if exists #tmp

select 
  s.bank_date_last [last_wire]
  , datefromparts(year(a.final_disposition_date),month(a.final_disposition_date),1) [collection_period]
  , a.asset_id
  , a.name_simple
  , a.investment_payment
  , 'UAM' [source_acct]
  , s.total_cash_received
  , S.settlement_costs
  , s.cash_to_remit_to_coll_calc
  , s.cash_to_remit_to_coll_calc+settlement_costs-s.total_cash_received [remaining_cash_delta]
  , acct.name [acct_name]
  , b.[date] [date_transferred_to_collections]
  , s.bank_descr_last
  , s.note_last
  
  , s.cost_basis_program
  INTO #TMP
  from 
  vSettlementsEx s
  join vAssetsEx a on a.asset_id = s.asset_id
  left join vPositionsAll p on p.asset_id = a.asset_id
  left join vAccounts acct on acct.account_id = p.account_id
  left join vBankTransEx b on (s.cash_to_remit_to_coll_calc between b.net_amount-1 and b.net_amount+1) and b.bankacct_id = acct.bankacct_id_coll
  
    where 
      p.is_unlock = 0 and p.is_trade=0
      and convert(date,a.final_disposition_date) >= @bom
      and a.final_disposition_date is not null
  ORDER BY
    s.bank_date_last desc

SELECT
  count(*) [#]
  , collection_period
  , acct_name
  , sum(cash_to_remit_to_coll_calc) [cash_to_remit_to_coll_|#,##0.00|]
  from #tmp
  group by 
    collection_period
    , acct_name
  order by collection_period DESC
    
SELECT
  collection_period
  , last_wire
  , asset_id
  , name_simple
  , investment_payment [orig_investment_amt_|#,##0||]
  , source_acct
  , total_cash_received [total_cash_received_|#,##0.00||]
  , settlement_costs [uam_revenue_|#,000.00|]
  , cash_to_remit_to_coll_calc [cash_to_remit_to_coll_calc_|#,##0.00||]
  , remaining_cash_delta [remaining_cash_delta_|#,##0.00||]
  , acct_name
  , date_transferred_to_collections
  , bank_descr_last
  , cost_basis_program
  , note_last
  FROM #TMP

  ORDER BY LAST_WIRE DESC

DROP TABLE #TMP


--- FILE: ReportRunner\ReportRunner\SQL\DisposedAssetSummary.sql ---
declare @bom DATE


select @bom =DATEADD(day, -@days_back, dbo.TodayNY()) 

drop table if exists #tmp

select 
  a.asset_id
  , a.address_simple
  , a.name_Simple
  , a.age
  , a.investment_payment
  , s.settlement_type
  , s.settlement_reason
  , a.effective_date
  , a.final_disposition_date
  , p.account
  , p.wavg_buy_price [buy_price_|0.000|]
  , s.price_calc*100.0 [payoff_price]
  , s.cost_basis_program
  , s.age_at_termination
  , p.orig_buy_total_proceeds [purchase_proceeds]
  , cash_to_remit_to_coll_calc [cash_due_investor_$]
  , cash_to_remit_to_coll_calc-p.orig_buy_total_proceeds [simple_pl_$]
  into #tmp
  from 
  vSettlementsEx s
  join vAssetsEx a on a.asset_id = s.asset_id
  left join vPositionsAll p on p.asset_id = a.asset_id
    where 
      p.is_unlock = 0 and p.is_trade = 0
      and convert(date,a.final_disposition_date) >= @bom
    ORDER BY A.FINAL_DISPOSITION_DATE desc
     

SELECT 
  count(*) [#]
  , format(final_disposition_date,'MMM') [month]
  , account
  , sum(age_at_termination*investment_payment)/sum(investment_payment) [avg_age_|0|]
  , sum(payoff_price*investment_payment)/sum(investment_payment) [wavg_payoff_price_|0.000|]
  , sum(cash_due_investor_$) [cash_due_investor_$]
  , sum(simple_pl_$) [simple_pl_$] 
  from #tmp 
    group by 
    format(final_disposition_date,'MMM') 
    , account
    order by format(final_disposition_date,'MMM') desc


SELECT 
  count(*) [#]
  , settlement_type
  , settlement_reason
  from #tmp 
  group by settlement_type, settlement_reason
  order by settlement_type, settlement_reason
    

SELECT * FROM #TMP order by final_disposition_date asc


drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\DLQSummaryByAccount.sql ---
BEGIN TRANSACTION

  DROP TABLE IF EXISTS #tmp_dlq

  DECLARE @cutoff as date
  DECLARE @orig_cutoff as date

  SET @cutoff = EOMONTH(GETDATE(),-1)  

  SELECT @orig_cutoff = g.[value] FROM Globals g WHERE g.[key] = 'CUTOFF'

  
  UPDATE globals SET [value] = CONVERT(varchar,@cutoff,101) WHERE [key] = 'CUTOFF'

   
  SELECT @cutoff [Cutoff]
  ,c.latest [Last Credit Date] FROM (SELECT max(asOf) [latest] FROM vCreditFiles WHERE latest_api = 1 HAVING count(*)>1000) c 

  SELECT
     ex.asset_id [asset_id]
    ,ex.max_id [max_id]
    ,p.account [account]
    ,ex.investment_payment [investment_payment]
  
    ,ex.lien_position [unlock lien position]
    ,ex.effective_date [effective date]
    ,d.cr_asof [credit load date]
    ,d.cr_date_reported [credit report date]
    ,d.paystring_full [credit pay string]
    ,case when d.mtg_dlq_rank_status_code_worst >= 2 or d.any_bk_or_fcl = 1 then 'TRUE' when (d.mtg_dlq_rank_status_code_worst is null and ex.lien_position != 1) then null else 'FALSE' end [is_dlq]
    ,case 
      when ex.lien_position = 1 then 'NO MTG' 
      when d.mtg_dlq_rank_status_code_worst >= 1 and cas.label is not null then cas.label
      when d.any_bk_or_fcl = 1 then  csc.status_code
     end [dlq_status]
    , case when ex.lien_position = 1 then 'NO MTG' when  d.mtg_dlq_rank_status_code_worst >= 1 or d.any_bk_or_fcl = 1 then isnull(cas.label,'') + '/' + isnull(csc.status_code,'') else null end [dlq_acct_status_and_status_code]
  into #tmp_dlq  
    
  FROM dbo.vAssetsExCutoff ex
    JOIN dbo.vAssetsPositionEx p on ex.asset_id=p.asset_id
    JOIN dbo.vDebtAgg d on ex.asset_id = d.asset_id
      LEFT JOIN vCRAccountStatus cas on cas.mtg_dlq_rank = d.mtg_dlq_rank_account_status_worst
      LEFT JOIN CRStatusCodes csc on csc.mtg_dlq_rank = d.mtg_dlq_rank_status_code_worst

    WHERE (ex.final_disposition_date is null or ex.final_disposition_date <= @cutoff)


 
 SELECT 
   account [account         ]    
   
   ,sum(case when [dlq_status] = '90' THEN 1 ELSE 0 END) [  90 ]
   ,sum(case when [dlq_status] = '120+' THEN 1 ELSE 0 END) [  120+  ]
   ,sum(case when [dlq_status] = '7' THEN 1 ELSE 0 END)  [  BK  ]
   ,sum(case when [dlq_status] = 'FCL' THEN 1 ELSE 0 END) [  FCL  ]
  FROM #tmp_dlq  
   WHERE dlq_status is not null
   and account not in ('UAH 1', 'URIT')
 GROUP BY account
  


  
 SELECT * FROM #tmp_dlq  
   WHERE dlq_status is not null 
   and is_dlq = 'TRUE'
   and account not in ('UAH 1', 'URIT')
   order by account desc, dlq_status asc
  
    
  UPDATE dbo.globals SET [value] = CONVERT(varchar,@orig_cutoff,101) WHERE [key] = 'CUTOFF'

  DROP TABLE IF EXISTS #tmp_dlq
  
COMMIT TRANSACTION


--- FILE: ReportRunner\ReportRunner\SQL\DocumentCustodianDailySummary.sql ---
declare @runDate datetime = dbo.TodayNY()  








DROP TABLE IF EXISTS #tmp_vendors

select 
    vendors.vendor_id, 
    vendors.[name]
    into #tmp_vendors
        from vVendors vendors 
            join VendorTypes vendorTypes 
              on vendors.vendortype_id = vendorTypes.id 
              and vendorTypes.id = 5
              and (vendors.[name] = @vendor or @vendor = 'ALL') 

select STRING_AGG(vendors.[name],',') as 'Custodians'
  from #tmp_vendors vendors





select distinct
  vendors.[name]
  ,shipment.tracking_number
  ,shipment.tracking_url
  ,shipment.nice_name
  
from vCollatShipmentsEx shipment
    join #tmp_vendors vendors on shipment.doccustodian_id = vendors.vendor_id

where 
  shipment.ship_date = @runDate 
  and shipment.shipped = 1
order by 
  vendors.[name]
  ,shipment.tracking_number






select 
  vendors.[name]
  ,shipment.tracking_number
  ,shipment.asset_id
  ,shipment.name_simple
  ,shipment.address_simple
  ,shipment.doc_name

  ,va.trade_id
  ,va.account                   
from vCollatShipmentsEx shipment
    join #tmp_vendors vendors on shipment.doccustodian_id = vendors.vendor_id
    left outer join vTradesAll va on shipment.asset_id = va.asset_id and va.latest_td = 1 and va.is_unlock = 0

where 
  shipment.ship_date = @runDate 
  and shipment.shipped = 1

order by 
  vendors.[name]
  ,shipment.tracking_number
  ,shipment.name_simple
  ,shipment.address_simple
  ,shipment.doc_name

DROP TABLE IF EXISTS #tmp_vendors


--- FILE: ReportRunner\ReportRunner\SQL\DuplicateAssetsCheck.sql ---
select distinct 'vAssetsExCutoff' [view], asset_id, count(*) [count]  FROM vAssetsExCutoff group by asset_id having count(*)>1
union
select distinct 'vAssetsEx' [view], asset_id, count(*) [count]  FROM vAssetsEx group by asset_id having count(*)>1
union
select distinct 'vSettlements' [view], asset_id, count(*) [count]  FROM vSettlements group by asset_id having count(*)>1
union
select distinct 'vPositionsAllTDCutoff' [view], asset_id, count(*) [count]  FROM vPositionsAllTDCutoff where remaining_investment_payment !=0 group by asset_id having count(*)>1


--- FILE: ReportRunner\ReportRunner\SQL\EligibleCollateral.sql ---
exec dbo.CollatReadyForSale @account_id=@account_id, @guideline_id=@guideline_id, @process_exceptions=@process_exceptions, @show_summary=@show_summary, @show_doc_status=@show_doc_status, @show_trade_ticket_copy_paste=@show_trade_ticket_copy_paste, @show_detail=@show_detail, @show_exception_detail=@show_exception_detail, @only_eligible=@only_eligible


--- FILE: ReportRunner\ReportRunner\SQL\ExpenseBreakdown.sql ---
DROP TABLE IF EXISTS #tmp

select a.asset_id,full_name,account_name,type,status,reference_id,date,amount[amount_|#,###.##|],payer,vendor_name,reimbursable,unpaid_owner_obligation,invoice_file
into #tmp from vExpensesEx e
join vAssetsEx a on e.asset_id = a.asset_id

select * from #tmp where status='Open' order by account_name,status,date
select * from #tmp where status='Reimbursed by Investor' order by account_name,status,date
select * from #tmp where status='Refunded' order by account_name,status,date

DROP TABLE #tmp


--- FILE: ReportRunner\ReportRunner\SQL\FinderSummary-MissionControl.sql ---
DROP TABLE IF EXISTS #TMP

SELECT distinct
  p.pipeline_id
  , p.asset_id
  , p.name
  , p.opp_source_txt [partner]
  , p.first_contact
  , p.last_update
  , datediff(d,p.first_contact,last_update) [days_in_pipeline]
  , datediff(d,p.last_update,dbo.GetDateNY()) [days_since_last_update]
  , p.group_name
  , p.investment_payment
  , convert(float,null) finders_fee
  , convert(date,null) date_paid
  , convert(date,null) effective_date
  , mss.[rank]
  , p.sub_stage
  , p.loss_reason
  , p.sales
  , max_profile.PHONE as phone
  , max_profile.EMAIL as email
  INTO #TMP
    FROM 
      vPipelineEx p
      left join MondaySubStages mss on mss.sub_stage = p.sub_stage
	  left join API_APPLICATION max_app on p.pipeline_id = max_app.MONDAY_PULSE_ID 
	  left join API_APPLICATIONPROFILE max_appprofile on max_appprofile.APPLICATION_ID = max_app.id 
	  left join API_PROFILE max_profile on max_profile.id = max_appprofile.PROFILE_ID
    where 
      p.partner_account_txt = @parnter
      and p.name !='Roberts - 1656 Fall Creek Rd, Kingsports, TN'
	  and max_appprofile.POSITION = 1
    order by 
     group_name
    , opp_source_txt





    





UPDATE p set days_since_last_update=datediff(d,last_update,dbo.GetDateNY()) from #tmp p 
UPDATE p set days_in_pipeline=datediff(d,first_contact,dbo.GetDateNY()) from #tmp p 

UPDATE p set finders_fee=a.finders_fee,effective_date=a.effective_date from #tmp p join vAssets a on a.asset_id=p.asset_id

update p set date_paid=b.date from #tmp p join vBankTrans b on b.net_amount=-finders_fee where b.bankacct_id = 1309823 and b.date between effective_date AND dateadd(m,1.5,effective_date) and descr like 'Withdrawal - Inclearing Check #%'
update p set date_paid=b.date from #tmp p join vBankTrans b on b.net_amount=-finders_fee where b.bankacct_id = 1309823 and date_paid is null and b.date between effective_date AND dateadd(m,1.5,effective_date) and descr like '%Wire%'
update p set date_paid=b.date from #tmp p join vBankTrans b on b.net_amount=-finders_fee where b.bankacct_id = 1309823 and date_paid is null and b.date between effective_date AND dateadd(m,2.5,effective_date)
update p set date_paid=b.TRANSACTION_DATE from #tmp p join FRBInv b on b.AMOUNT=-finders_fee where date_paid is null and b.TRANSACTION_DATE between effective_date AND dateadd(m,2.5,effective_date)
   
SELECT #TMP.name,partner,investment_payment [investment_payment_$],first_contact,last_update,days_in_pipeline,days_since_last_update,sub_stage,sales,phone,email FROM #TMP where group_name = 'Active Pipeline' order by rank desc, days_since_last_update asc
SELECT [name],partner,investment_payment,first_contact,last_update,days_in_pipeline,days_since_last_update,sub_stage,sales,phone, Email FROM #TMP where group_name = 'Paused Deals' order by days_since_last_update asc
SELECT asset_id,[name],partner,investment_payment,first_contact,effective_date [origination_date],finders_fee [finders_fee_$],date_paid date_payment_cashed,sales FROM #TMP where group_name = 'Won' ORDER BY effective_date desc
SELECT [name],partner,investment_payment,first_contact,last_update,days_in_pipeline,days_since_last_update,loss_reason,sales,phone, Email FROM #TMP where group_name = 'Lost' ORDER BY DAYS_SINCE_LAST_UPDATE ASC


DROP TABLE #TMP


--- FILE: ReportRunner\ReportRunner\SQL\FinderSummary.sql ---
if @parnter = 'NewVisionDirect' 
	begin
	update Pipeline set partner_account_txt  = 'NewVisionDirect' where partner_account_txt  = 'Ocean Park Financial'
	end

if @parnter = 'Barastone' 
	begin
	update Pipeline set partner_account_txt  = 'Barastone' where opp_source_txt = 'Mark Rogers' and partner_account_txt is null
	end


DROP TABLE IF EXISTS #TMP_Monday
DROP TABLE IF EXISTS #TMP_Max
DROP TABLE IF EXISTS #TMP

SELECT distinct
	p.partner_account_txt 
  , opp_source_txt
  , p.pipeline_id
  , p.asset_id
  , replace(p.name, ', ,','') as name
  , p.opp_source_txt [partner]
  , p.first_contact
  , p.last_update
  , datediff(d,p.first_contact,last_update) [days_in_pipeline]
  , datediff(d,p.last_update,dbo.GetDateNY()) [days_since_last_update]
  , p.group_name
  , (case when p.investment_payment is not null then p.investment_payment else investment_payment_requested end) as investment_payment 
  , convert(float,null) finders_fee
  , convert(date,null) date_paid
  , convert(date,null) effective_date
  , mss.[rank]
  , p.sub_stage
  , p.loss_reason
  , p.sales_last_name as sales
  , max_app.id as application_id
  INTO #TMP_Max
    FROM 
      vPipelineEx p
      left join MondaySubStages mss on mss.sub_stage = p.sub_stage
	  left join API_APPLICATION max_app on convert(varchar(1024),p.pipeline_id) = max_app.MONDAY_PULSE_ID 

	  left join API_APPLICATIONPROFILE max_appprofile on max_appprofile.APPLICATION_ID = max_app.id 
	  left join API_PROFILE max_profile on max_profile.id = max_appprofile.PROFILE_ID
    where 
      p.partner_account_txt = @parnter


      and p.name !='Roberts - 1656 Fall Creek Rd, Kingsports, TN'

    order by 
     group_name
    , opp_source_txt

alter table #TMP_Max add phone varchar(128), email varchar(128)

update p set email = max_profile.EMAIL, phone = max_profile.PHONE
	from #TMP_Max p 
	join API_APPLICATIONPROFILE max_appprofile on max_appprofile.APPLICATION_ID = p.application_id
	join API_PROFILE max_profile on max_profile.id = max_appprofile.PROFILE_ID

delete from #TMP_Max where name = 'Denham -  , '

SELECT distinct
	p.partner_account_txt 
  , opp_source_txt
  , p.pipeline_id
  , p.asset_id
  , p.name
  , p.opp_source_txt [partner]
  , p.first_contact
  , p.last_update
  , datediff(d,p.first_contact,last_update) [days_in_pipeline]
  , datediff(d,p.last_update,dbo.GetDateNY()) [days_since_last_update]
  , p.group_name
  , p.investment_payment
  , convert(float,null) finders_fee
  , convert(date,null) date_paid
  , convert(date,null) effective_date
  , mss.[rank]
  , p.sub_stage
  , p.loss_reason
  , p.sales as sales
  , max_profile.PHONE as phone
  , max_profile.EMAIL as email
  INTO #TMP_Monday
    FROM 
      vPipelineEx_Monday p
      left join MondaySubStages mss on mss.sub_stage = p.sub_stage
	  left join API_APPLICATION max_app on convert(varchar(1024),p.pipeline_id) = max_app.MONDAY_PULSE_ID 

	  left join API_APPLICATIONPROFILE max_appprofile on max_appprofile.APPLICATION_ID = max_app.id 
	  left join API_PROFILE max_profile on max_profile.id = max_appprofile.PROFILE_ID
    where 
	  p.partner_account_txt = @parnter

      and p.name !='Roberts - 1656 Fall Creek Rd, Kingsports, TN'
	  and max_appprofile.POSITION = 1
	  and p.asset_id not in (select asset_id from #TMP_Max)
    order by 
     group_name
    , opp_source_txt

	select partner_account_txt, opp_source_txt, pipeline_id, asset_id, name, partner, first_contact, last_update, days_in_pipeline, days_since_last_update, group_name, investment_payment, finders_fee, date_paid, effective_date, rank, sub_stage, loss_reason, sales, phone, email
		into #tmp from #TMP_Max
	insert into #tmp (partner_account_txt, opp_source_txt, pipeline_id, asset_id, name, partner, first_contact, last_update, days_in_pipeline, days_since_last_update, group_name, investment_payment, finders_fee, date_paid, effective_date, rank, sub_stage, loss_reason, sales, phone, email)
		select partner_account_txt, opp_source_txt, pipeline_id, asset_id, name, partner, first_contact, last_update, days_in_pipeline, days_since_last_update, group_name, investment_payment, finders_fee, date_paid, effective_date, rank, sub_stage, loss_reason, sales, phone, email
	 from #TMP_Monday

DROP TABLE IF EXISTS #TMP_Monday
DROP TABLE IF EXISTS #TMP_Max





    





UPDATE p set days_since_last_update=datediff(d,last_update,dbo.GetDateNY()) from #tmp p 
UPDATE p set days_in_pipeline=datediff(d,first_contact,dbo.GetDateNY()) from #tmp p 

UPDATE p set finders_fee=a.finders_fee,effective_date=a.effective_date from #tmp p join vAssets a on a.asset_id=p.asset_id



update p set date_paid=b.date from #tmp p join vBankTrans b on b.net_amount=-finders_fee where b.bankacct_id = 1309823 and b.date between effective_date AND dateadd(m,1.5,effective_date) and descr like 'Withdrawal - Inclearing Check #%'
update p set date_paid=b.date from #tmp p join vBankTrans b on b.net_amount=-finders_fee where b.bankacct_id = 1309823 and date_paid is null and b.date between effective_date AND dateadd(m,1.5,effective_date) and descr like '%Wire%'
update p set date_paid=b.date from #tmp p join vBankTrans b on b.net_amount=-finders_fee where b.bankacct_id = 1309823 and date_paid is null and b.date between effective_date AND dateadd(m,2.5,effective_date)
update p set date_paid=b.date from #tmp p join vBankTrans b on abs(round(CONVERT(decimal(10,3),b.net_amount),2))=abs(round(CONVERT(decimal(10,3),finders_fee),2)) where b.bankacct_id = 1345938 and date_paid is null and b.date between effective_date AND dateadd(m,2.5,effective_date)

update p set date_paid=b.TRANSACTION_DATE from #tmp p join FRBInv b on b.AMOUNT=-round(CONVERT(decimal(10,3),finders_fee),2) where date_paid is null and b.TRANSACTION_DATE between dateadd(m,-1,effective_date) AND dateadd(m,2.5,effective_date)
   
SELECT #TMP.name,partner,investment_payment [investment_payment_$],first_contact,last_update,days_in_pipeline,days_since_last_update,sub_stage,sales,phone,email FROM #TMP where group_name = 'Active Pipeline' order by rank desc, days_since_last_update asc
SELECT [name],partner,investment_payment,first_contact,last_update,days_in_pipeline,days_since_last_update,sub_stage,sales,phone, Email FROM #TMP where group_name = 'Paused Deals' order by days_since_last_update asc
SELECT asset_id,[name],partner,investment_payment,first_contact,effective_date [origination_date],finders_fee [finders_fee_$],date_paid date_payment_cashed,sales FROM #TMP where group_name = 'Won' ORDER BY effective_date desc
SELECT [name],partner,investment_payment,first_contact,last_update,days_in_pipeline,days_since_last_update,loss_reason,sales,phone, Email FROM #TMP where group_name = 'Lost' ORDER BY DAYS_SINCE_LAST_UPDATE ASC


DROP TABLE #TMP


--- FILE: ReportRunner\ReportRunner\SQL\FirstAmericanLienReleases.sql ---
SELECT
    '''' + CAST(a.max_id AS VARCHAR(50)) AS [Asset ID],
    a.account AS [Account Investor],
    a.settlement_type AS [Settlement Type],

    
    
    
    a.first_name AS [Borrower First Name],
    a.last_name AS [Borrower Last Name],

    
    
    
    a.address_1 AS [Property Address],
    a.city AS [Property City],
    a.state AS [Property State],
    a.zip AS [Property Postal Code],

    
    
    
    a.investment_payment AS [Initial Investment Payment],
    a.effective_date AS [Performance Deed/Mortgage Date],
    a.final_disposition_date AS [Payoff Date (Disposition Date)],

    
    
    

    CASE 
        WHEN app.mailing_address_1 IS NOT NULL THEN 'MAILING'
        ELSE 'HEI ADDRESS'
    END AS [Address Type],

    CASE 
        WHEN app.mailing_address_1 IS NOT NULL THEN app.mailing_address_1
        ELSE a.address_1
    END AS [Borrower Mailing Address],

    CASE 
        WHEN app.mailing_address_1 IS NOT NULL THEN app.mailing_address_2
        ELSE a.address_2
    END AS [Borrower Mailing Street Address 2],

    CASE 
        WHEN app.mailing_address_1 IS NOT NULL THEN app.mailing_city
        ELSE a.city
    END AS [Borrower Mailing City],

    CASE 
        WHEN app.mailing_address_1 IS NOT NULL THEN app.mailing_state
        ELSE a.state
    END AS [Borrower Mailing State],

    CASE 
        WHEN app.mailing_address_1 IS NOT NULL THEN app.mailing_zip
        ELSE a.zip
    END AS [Borrower Mailing Postal Code]

FROM dbo.vAssetsPositionEx a
LEFT JOIN vApplicantsEx app 
    ON app.asset_id = a.asset_id
    AND app.applicanttype_id = 1   
RIGHT JOIN vSettlementsEx s
    ON s.asset_id = a.asset_id
WHERE s.lien_release_submitted is null
  
ORDER BY a.final_disposition_date ASC


--- FILE: ReportRunner\ReportRunner\SQL\flood_insurance_issues.sql ---
select a.asset_id, a.effective_date, a.name_simple, a.address_full
	, (case flood_zone when 1 then 'Yes' when 0 then 'No' else 'No Data' end) as flood_zone
	, isnull(h.INSURANCE_TYPE, 'No Data') as Insurance_Status
from vAssetsex a
left join vPipeline p on p.asset_id = a.asset_id
left join api_hoi h on h.APPLICATION_ID = p.application_id and INSURANCE_TYPE = 'flood'
where a.effective_date >='1/1/2023'
and a.flood_zone =1
and INSURANCE_TYPE is null
order by a.effective_date asc



select a.asset_id, a.effective_date, a.name_simple, a.address_full
	, (case flood_zone when 1 then 'Yes' else 'No' end) as flood_zone
	, isnull(h.INSURANCE_TYPE, 'No Data') as Insurance_Status
from vAssetsex a
left join vPipeline p on p.asset_id = a.asset_id
left join api_hoi h on h.APPLICATION_ID = p.application_id 
where a.effective_date >='1/1/2023'
and isnull(a.flood_zone,0) =0
and INSURANCE_TYPE = 'flood'
order by a.effective_date asc


--- FILE: ReportRunner\ReportRunner\SQL\funded_not_shipped.sql ---
select p.account, n.* 
  from dbo.vFundings_New n 
    join dbo.vPositions p  on n.asset_id = p.asset_id
  where n.funding_status != 'Cancelled' and n.funding_type = 'Deal' and n.value_date >= '12/03/2024'
      and n.asset_id not in (
      select distinct ship.asset_id
          from vCollatShipmentDetailEx ship
      where (asof >='6/1/2023'
  and shipped =1
  and doc_custodian_name in('wsfs','us bank')
  and type = 'Digital'
  ))
  and n.value_date <= dateadd(day,-2,getdate())


--- FILE: ReportRunner\ReportRunner\SQL\funding_summary_breakdown.sql ---
declare	@p_StartDate date
declare	@p_EndDate date


if @p_EndDate is null 
	select @p_EndDate = max(value_date) from Fundings_New

if @p_StartDate is null 
	select @p_StartDate = DATEADD(week,-5, @p_EndDate)


	declare @v_EndDate date

	set @v_EndDate  = @p_StartDate

	if @p_EndDate is not null 
		set @v_EndDate  = @p_EndDate

	drop table if exists #tmp

	select cl.asset_id
		, fund.value_date as funding_date
		, fund.funding_status
		, fund.amount [investment_payment]
		, cl.file_num as file_num
		, cl.customer_pipeline_label
		, cl.origination_fee
    , cl.pre_paid_fees
	into #tmp
	from vFundings_New fund 
	left join Closing cl on fund.asset_id = cl.asset_id 
	where fund.value_date between @p_StartDate and @v_EndDate

		select 
		  funding_date
		, (select count(*) from Fundings_New fund where fund.value_date = #tmp.funding_date and fund.fundingstatus_id <> 4) as total_fundings_for_day
		, dbo.BizDayDiff(funding_date,dbo.TodayNY()) as weekdays_since_funding
		, funding_status
		, sum(investment_payment) as investment_payment_$
		, sum(origination_fee) as origination_fee_$ 
		, sum(pre_paid_fees) as pre_paid_fees_$ 
	from #tmp
	where funding_status <> 'Cancelled'
	group by funding_date
		, dbo.BizDayDiff(funding_date,dbo.TodayNY())
		, funding_status
  order by funding_date desc

	select 
		  asset_id
		, funding_date
		, dbo.BizDayDiff(funding_date,dbo.TodayNY()) as weekdays_since_funding
		, funding_status
		, file_num
		, customer_pipeline_label
		, investment_payment as investment_payment_$
		, origination_fee as origination_fee_$ 
		, pre_paid_fees as pre_paid_fees_$ 
	from #tmp
	where funding_status <> 'Cancelled'
	order by funding_date desc, asset_id asc

	drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\HistoricalOrigination-extended.sql ---
drop table if exists #tmp

select 1 [count]
, datepart(year,effective_date) [year]
, dbo.QuarterDate(effective_date) [quarter]
,convert(date,format(effective_date,'M/1/yyyy')) [month]
, investment_payment
,max_id
,a.asset_id
,city_state_zip
,starting_home_value
,effective_date
,final_disposition_date
,cost_limit
,exchange_rate
,state
,origination_fee
,a.investment_pct+a.ltv [cltv]
,a.total_home_finance
,a.total_home_finance_limit
,ISNULL(gain_on_sale,0) [GAIN_ON_SALE] 
into #tmp FROM vAssetsEx a 
  left join vTradesGOS g on g.asset_id = a.asset_id
where effective_date <= (select convert(varchar(10), EOMONTH(dateadd(month,-1,getdate())), 101))

select 
  sum([count]) [#]
  ,sum(investment_payment) [investment_payment_$]
  ,sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|]
  ,sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] 
  ,sum(investment_payment*cltv)/sum(investment_payment) [wavg_cltv_|0.00|]
  ,sum(investment_payment*total_home_finance)/sum(investment_payment) [wavg_thf_|0.00|]
  ,sum(investment_payment*total_home_finance_limit)/sum(investment_payment) [wavg_thfl_|0.00|]
  ,sum(investment_payment)/sum([count]) [avg_investment_payment_$]

  from #tmp

select 
  sum([count]) [#]
  ,year
  ,sum(investment_payment) [investment_payment_$]
  ,sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|]
  ,sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] 
  ,sum(investment_payment*cltv)/sum(investment_payment) [wavg_cltv_|0.00|]
  ,sum(investment_payment*total_home_finance)/sum(investment_payment) [wavg_thf_|0.00|]
  ,sum(investment_payment*total_home_finance_limit)/sum(investment_payment) [wavg_thfl_|0.00|]
  ,sum(investment_payment)/sum([count]) [avg_investment_payment_$]

from #tmp group by year order by year desc


select 
  sum([count]) [#]
  ,quarter
  ,sum(investment_payment) [investment_payment_$]
  ,sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|]
  ,sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] 
  ,sum(investment_payment*cltv)/sum(investment_payment) [wavg_cltv_|0.00|]
  ,sum(investment_payment*total_home_finance)/sum(investment_payment) [wavg_thf_|0.00|]
  ,sum(investment_payment*total_home_finance_limit)/sum(investment_payment) [wavg_thfl_|0.00|]
  ,sum(investment_payment)/sum([count]) [avg_investment_payment_$]

from #tmp group by quarter order by quarter desc


select 
  sum([count]) [#]
  ,month
  ,sum(investment_payment) [investment_payment_$]
  ,sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|]
  ,sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] 
  ,sum(investment_payment*cltv)/sum(investment_payment) [wavg_cltv_|0.00|]
  ,sum(investment_payment*total_home_finance)/sum(investment_payment) [wavg_thf_|0.00|]
  ,sum(investment_payment*total_home_finance_limit)/sum(investment_payment) [wavg_thfl_|0.00|]
  ,sum(investment_payment)/sum([count]) [avg_investment_payment_$]

from #tmp group by month order by month desc

select 
  max_id
  ,asset_id
  ,effective_date
  ,city_state_zip
  ,starting_home_value
  ,investment_payment
  ,cost_limit
  ,exchange_rate
  ,final_disposition_date
  ,cltv
  ,total_home_finance
  ,total_home_finance_limit
  ,gain_on_sale 
from #tmp

select 
  sum([count]) [#]
  ,month
  ,state
  ,sum(investment_payment) [investment_payment_$]
  ,sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|]
  ,sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|]
  ,sum(investment_payment*cltv)/sum(investment_payment) [wavg_cltv_|0.00|]
  ,sum(investment_payment*total_home_finance)/sum(investment_payment) [wavg_thf_|0.00|]
  ,sum(investment_payment*total_home_finance_limit)/sum(investment_payment) [wavg_thfl_|0.00|]  
  ,sum(investment_payment)/sum([count]) [avg_investment_payment_$]
  ,sum(origination_fee) [origination_fee_$]
  ,sum(gain_on_sale) [gain_on_sale_$] 
from #tmp group by month,state order by month desc,state


drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\HistoricalOrigination.sql ---
drop table if exists #tmp

select 1 [count], datepart(year,effective_date) [year], dbo.QuarterDate(effective_date) [quarter],convert(date,format(effective_date,'M/1/yyyy')) [month], investment_payment,max_id,a.asset_id,city_state_zip,starting_home_value,effective_date,final_disposition_date,cost_limit,exchange_rate,state,origination_fee,ISNULL(gain_on_sale,0) [GAIN_ON_SALE] into #tmp FROM vAssetsEx a left join vTradesGOS g on g.asset_id = a.asset_id
where effective_date <= (select convert(varchar(10), EOMONTH(dateadd(month,-1,getdate())), 101))

select sum([count]) [#], sum(investment_payment) [investment_payment_$],sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|],sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] from #tmp
select sum([count]) [#],year, sum(investment_payment) [investment_payment_$],sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|],sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] from #tmp group by year order by year desc
select sum([count]) [#],quarter, sum(investment_payment) [investment_payment_$],sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|],sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] from #tmp group by quarter order by quarter desc
select sum([count]) [#],month, sum(investment_payment) [investment_payment_$],sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|],sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|] from #tmp group by month order by month desc

select max_id,asset_id,effective_date,city_state_zip,starting_home_value,investment_payment,cost_limit,exchange_rate,final_disposition_date,gain_on_sale from #tmp

select sum([count]) [#],month, state,sum(investment_payment) [investment_payment_$],sum(investment_payment * cost_limit)/sum(investment_payment) [wavg_cost_limit_|0.00%|],sum(investment_payment*exchange_rate)/sum(investment_payment) [wavg_exchange_rate_|0.00|],sum(origination_fee) [origination_fee_$],sum(gain_on_sale) [gain_on_sale_$] from #tmp group by month,state order by month desc,state


drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\IncorrectLNAmounts.sql ---
SELECT a.effective_date,i.collateral_key_delete [us_bank_asset_id],a.asset_id,a.name_simple,a.address_simple,a.starting_home_value [starting_home_value_|$0,###|],a.investment_payment [investment_payment_|$0,###|],i.lnamount  [lnamount_|$0,###|],acct.doccustodian_id INTO #TMP 
FROM 
  vAssetsEx a 
  join vCollatInv i on a.asset_id = i.asset_id 
  left join vPositions p on p.asset_id = a.asset_id
  left join vAccounts acct on acct.account_id = p.account_id 
  
  where (i.lnamount != a.INVESTMENT_PAYMENT AND i.latest = 1) and (acct.doccustodian_id is null or acct.doccustodian_id = 10) order by effective_date desc

SELECT * FROM #TMP

SELECT 
  a.asset_id [agreement_#]
  , a.effective_date
  , a.expiration_date [expiration_date]
  , a.apn [property_apn]
  , a.name_simple [property_owner]
  , a.occupancy_type [property_occupancy]
  , a.address_simple [property_address]
  , a.city [property_city]
  , a.state [property_state]
  , a.zip [property_zip]
  , a.starting_home_value
  , a.investment_payment
  , a.investment_pct
  , a.exchange_rate
  , a.unlock_pct
  , a.cost_limit [annualized_cost_limit]
  , a.total_home_finance_limit [home_finance_limit]
  , convert(bit,a.doc_consent_of_spouse) [doc_include_consent_of_spouse]
  , convert(bit,0) [doc_include_title_insurance]
  , convert(bit,1) [doc_include_title_report]
  
  FROM 
    vAssetsEx a
    join #tmp ass on ass.asset_id = a.asset_id
    

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\InvestorBalances.sql ---
select 
  count(*) [num_assets]
  , account
  , sum(orig_buy_investment_payment) [orig_inv_pmt_|0,###|]
  , sum(remaining_investment_payment) [remaining_investment_payment_|0,###|] 
  , sum(remaining_investment_payment)-sum(orig_buy_investment_payment) [sold_or_paidoff_|0,###|]
  from 
    vPositionsAll p
    where
      p.account_id = 4
      and p.remaining_investment_payment != 0
      group by account
    order by count(*) desc
    
    
    select 
      p.asset_id
      , a.name_simple
      , a.address_full
      , orig_buy_investment_payment [orig_inv_pmt_|0,###|]
      , remaining_investment_payment [remaining_investment_payment_|0,###|] 
      , remaining_investment_payment-orig_buy_investment_payment [sold_or_paidoff_|0,###|]
      , p.last_trade
      , a.effective_date
      from 
      vPositionsAll p join vAssetsEx a on p.asset_id = a.asset_id where account_id = 4


--- FILE: ReportRunner\ReportRunner\SQL\InvestorTapes.sql ---
DROP TABLE IF EXISTS #TMP

select
t.trade_date [trade_date]
, t.settle_date [settle_date]
, t.trade_id [trade_id]
, t.asset_id
, a.address_full
, a.name_simple
, a.starting_home_value
, t.oface [investment_payment]
, a.investment_payment/a.starting_home_value [investment_pct]
, a.exchange_rate
, a.investment_payment/a.starting_home_value*a.exchange_rate [unlock_pct]
, 1.06 [base_price]
, a.base_exchange_rate
, 1.06-t.price/100.0 [price_adj]
, t.price/100.0 [price]
, t.total_proceeds
, 'Active' [begin_collection_period]
, 'Active' [end_collection_period]
, null [termination_date]
, null [payoff_amount]
, null [gross_asset_price]
, null [asset_duration_days]
, null [mgr_incentive_fee_hurdle]
, null [mgr_incentive_fee]
, null [disposition_fee]
, null [proceeds_qualified_as_available_funds]
, a.home_value_hpi_latest
, a.valuation_asOf_latest
, a.valuation_type_latest
, a.age_at_origination_primary
, a.age [hea_age]
, 'TBD' [unlock_share_estimate]
, a.effective_date
, a.origination_fee
, a.origination_fee_pct
, a.cost_limit
, a.cost_limit_basis
, a.term
, 1.06 [base_price_hardcoded]
, a.earliest_valuation_value [original_avm]
, a.valuation_value_latest [current_avm]
, a.hpi_index_calc

INTO #TMP
  from
    vTrades t
    join vAssetsEx a on a.asset_Id = t.asset_Id
  where
    t.account_id = 5
    and t.buy_sell = 'B'
    and (t.settle_date <= @cutoff or @cutoff is null)
  ORDER BY
    trade_id, name_simple





SELECT TRADE_DATE,ASSET_ID,NAME_SIMPLE,ADDRESS_FULL,EFFECTIVE_DATE,STARTING_HOME_VALUE,INVESTMENT_PAYMENT,INVESTMENT_PCT,EXCHANGE_RATE,UNLOCK_PCT,ORIGINATION_FEE_PCT,COST_LIMIT,COST_LIMIT_BASIS,TERM,BASE_PRICE_HARDCODED,TOTAL_PROCEEDS [PURCHASE_PROCEEDS],original_avm,CURRENT_AVM,hpi_index_calc [PCT_CHANGE] FROM #TMP order by trade_id,name_simple


select TRADE_DATE, SETTLE_DATE, TRADE_ID, ASSET_ID, ADDRESS_FULL, NAME_SIMPLE, STARTING_HOME_VALUE, INVESTMENT_PAYMENT, INVESTMENT_PCT, EXCHANGE_RATE, UNLOCK_PCT, BASE_PRICE, BASE_EXCHANGE_RATE, PRICE_ADJ, PRICE, TOTAL_PROCEEDS, BEGIN_COLLECTION_PERIOD, END_COLLECTION_PERIOD, TERMINATION_DATE, PAYOFF_AMOUNT, GROSS_ASSET_PRICE, ASSET_DURATION_DAYS, MGR_INCENTIVE_FEE_HURDLE, MGR_INCENTIVE_FEE, DISPOSITION_FEE, PROCEEDS_QUALIFIED_AS_AVAILABLE_FUNDS, HOME_VALUE_HPI_LATEST, valuation_asOf_latest, VALUATION_TYPE_LATEST, AGE_AT_ORIGINATION_PRIMARY, HEA_AGE, UNLOCK_SHARE_ESTIMATE FROM #TMP order by trade_id,name_simple
    
DROP TABLE #TMP


--- FILE: ReportRunner\ReportRunner\SQL\InvPmtMismatch.sql ---
SELECT

t.asset_id
,a.name_simple
,a.address_1
,t.net_oface [trade_remaining_nvestment_payment]
,a.investment_payment [asset_investment_payment]
,t.net_oface - a.investment_payment [delta]
FROM
 vAssetsEx a JOIN (select asset_id,sum(net_oface) [net_oface] from vTrades t group by asset_id)   t ON t.asset_id = a.asset_id
WHERE
 abs(a.investment_payment - t.net_oface) > 0.01
 and a.final_disposition_date is null
 and a.uw_issue_include_in_reporting_flag=1

order by 
  name_simple


--- FILE: ReportRunner\ReportRunner\SQL\JackedAssets.sql ---
drop table if exists #tmp
drop table if exists #summary
drop table if exists #diffs

select dateadd(d,1,added_to_badger) [processing_period_end],* into #tmp from vAssetsEx a where added_to_badger >= '1/1/2022' and a.final_disposition_date is null and a.asset_id not in ('92319226505632','50602697275745','23993534752096','40511385596129','79811061581131','46166212955905','97050521943264','97275394661238','97319887489573','21230489959647','99105789848805','75868222523291','48320833149070')  



 SELECT 
    t.asset_id [asset_id]
  , t.added_to_badger
  , t.processing_period_end
  , t.name_simple
  , t.investment_payment [investment_payment_current]
  , a.investment_payment [investment_payment_orig]
  , convert(float,null) [investment_payment_at_trade]
  , a.effective_date [effective_date_current]
  , convert(date,null) [effective_date_at_trade]
  , a.effective_date [effective_date_orig]
  , t.cost_limit [cost_limit_current]
  , a.cost_limit [cost_limit_orig]
  , convert(float,null) [cost_limit_at_trade]
  , t.exchange_rate [exchange_rate_current]
  , a.exchange_rate [exchange_rate_orig]
  
  , convert(float,null) [exchange_rate_at_trade]
  , t.total_home_finance_limit [total_home_finance_limit_current]
  , a.total_home_finance_limit [total_home_finance_limit_orig]
  , convert(float,null) [total_home_finance_limit_at_trade]
  , p.account [current_owner]
  , p.account_id [current_owner_id]
  
  , convert(datetime,null) [trade_date]
  
  , convert(varchar(30),null) [count_of_jacked_items]
  
  
  , convert(varchar(30),null) [jacked_items_on_trade]
  , convert(varchar(30),null) [jacked_items_on_fixed]
  
  into #diffs
  FROM 
   #tmp t
   join Assets_history a on a.id = t.asset_id and processing_period_end between valid_from and valid_to
   join vPositions p on p.asset_id = t.asset_id
   
  where
    (t.investment_payment != a.investment_payment_current)
    or
    (t.cost_limit != a.cost_limit)
    or
    (t.exchange_rate != a.exchange_rate)
    or
    (t.total_home_finance_limit != a.total_home_finance_limit)
    or
    (t.effective_date != a.effective_date)
   
  update d set d.investment_payment_at_trade = a.investment_payment, d.cost_limit_at_trade = a.cost_limit, d.exchange_rate_at_trade = a.exchange_rate, d.total_home_finance_limit_at_trade = a.total_home_finance_limit, d.trade_date=tr.trade_date, d.effective_date_at_trade=a.effective_date from #diffs d join vTrades tr on tr.asset_id = d.asset_id and tr.account_id = d.current_owner_id and buy_sell ='B' join Assets_history a on a.id = d.asset_id and tr.update_time between valid_from and valid_to and current_owner_id not in (1)
  
  update d set jacked_items_on_trade = case when investment_payment_at_trade != investment_payment_current then 'INV PMT. + ' else '' end + case when cost_limit_at_trade != cost_limit_current then 'ACL + ' else '' end + case when exchange_rate_at_trade != exchange_rate_current then 'E.R. + ' else '' end + case when total_home_finance_limit_at_trade != total_home_finance_limit_current then 'THFL' else '' end + case when effective_date_at_trade != effective_date_current then 'Eff. Date' else '' end from #diffs d
  update d set jacked_items_on_fixed = case when investment_payment_orig != investment_payment_current then 'INV PMT. + ' else '' end + case when cost_limit_orig != cost_limit_current then 'ACL + ' else '' end + case when exchange_rate_orig != exchange_rate_current then 'E.R. + ' else '' end + case when total_home_finance_limit_orig != total_home_finance_limit_current then 'THFL' else '' end +  case when effective_date_at_trade != effective_date_current then 'Eff. Date' else '' end from #diffs d
  
  
  update d set jacked_items_on_trade = left(jacked_items_on_trade,len(jacked_items_on_trade)-3) from #diffs d where right(jacked_items_on_trade,3) = '+  ' and jacked_items_on_trade like '%+%'
  update d set jacked_items_on_trade = left(jacked_items_on_trade,len(jacked_items_on_trade)-2) from #diffs d where right(jacked_items_on_trade,2) = '+ ' and jacked_items_on_trade like '%+%'
  update d set jacked_items_on_trade = '(FIXED BEFORE TRADE)' from #diffs d where len(jacked_items_on_trade) = 0
    

  select
   d.current_owner [account]
   , d.asset_id
   , d.trade_date
   , d.name_simple
   , d.investment_payment_current [investment_payment_current_$]
   , d.investment_payment_current-investment_payment_at_trade [investment_payment_$]
   , d.cost_limit_current-cost_limit_at_trade [cost_limit_|0.00%|]
   , d.exchange_rate_current-exchange_rate_at_trade [exchange_rate_|0.00|]
   , datediff(d,d.effective_date_current,effective_date_at_trade) [eff_date_days_diff]
   , d.total_home_finance_limit_current-total_home_finance_limit_at_trade [thf_|0.00%|]
   
   , jacked_items_on_trade

   from 
   #diffs d
   where 
   jacked_items_on_trade not like '%FIXED%'
   order by jacked_items_on_trade desc

  select
   d.current_owner [account]
   , d.asset_id
   , d.trade_date
   , d.name_simple
   , d.investment_payment_current [investment_payment_current_$]
   , d.investment_payment_current-investment_payment_orig [investment_payment_$]
   , d.cost_limit_current-cost_limit_orig [cost_limit_|0.00%|]
   , d.exchange_rate_current-exchange_rate_orig [exchange_rate_|0.00|]
   , d.total_home_finance_limit_current-total_home_finance_limit_orig [thf_|0.00%|]
   , datediff(d,d.effective_date_current,effective_date_at_trade) [eff_date_days_diff]
   , jacked_items_on_trade

   from 
   #diffs d
   where 
   jacked_items_on_trade  like '%FIXED%'
   order by jacked_items_on_trade desc

   
  select 
   
   d.jacked_items_on_trade
  , d.asset_id
  
  
  , d.investment_payment_current [investment_payment_current_$]
  , d.investment_payment_orig [investment_payment_orig_$]
  , d.investment_payment_at_trade [investment_payment_at_trade_$]
  , null [_]
  , d.cost_limit_current
  , d.cost_limit_orig
  , d.cost_limit_at_trade
  , null [_]
  , d.exchange_rate_current
  , d.exchange_rate_orig
  , d.exchange_rate_at_trade
  , null [_]
  , d.total_home_finance_limit_current
  , d.total_home_finance_limit_orig
  , d.total_home_finance_limit_at_trade
  , null [_]
  , d.effective_date_current
  , d.effective_date_orig
  , d.effective_date_at_trade
  , null [_]
  , d.current_owner
  
  , null [_]
  
  from 
    #diffs d
    
drop table if exists #tmp
drop table if exists #diffs
drop table if exists #summary


--- FILE: ReportRunner\ReportRunner\SQL\LA_Add.sql ---
declare @latest_load int
declare @latest_load_date date
select top 1 @latest_load = id,@latest_load_date=asOf from LALoads order by ASoF desc



select 
    '' + replace(A.asset_id,'/','.') [REF ID]
  , a.effective_date [OriginationDate]
  , convert(decimal(18,2),a.investment_payment) [OriginationLoanAmount]
  , a.first_name [Borrower1FName]
  , a.middle_name [Borrower1MName]
  , a.last_name [Borrower1LName]
  , a.ssn_last4 [Last4-digitSSN]
  
  , a.first_name_co [Borrower2FName]
  , a.middle_name_co [Borrower2MName]
  , a.last_name_co [Borrower2LName]
  , a.ssn_last4_co [Last4-digitSSN2]
  , a.address_simple [PropertyFullStreetAddress]
  , a.city [PropertyCity]
  , a.state [PropertyState]
  , a.zip [PropertyZip]
  , f.fips_code [FIPS]
  , a.apn [APN]
  
  
  from
    vAssetsEx a
    left join vFIPS f on a.state = f.state and a.county = f.county
  where
    not exists (select * from LAOut lo where lo.REF_ID = a.asset_id and lo.load_id = @latest_load)
    and final_disposition_date is null


--- FILE: ReportRunner\ReportRunner\SQL\LA_Add_Full_Population.sql ---
select 
    '' + replace(A.asset_id,'/','.') [REF ID]
  , a.effective_date [OriginationDate]
  , convert(decimal(18,2),a.investment_payment) [OriginationLoanAmount]
  , a.first_name [Borrower1FName]
  , a.middle_name [Borrower1MName]
  , a.last_name [Borrower1LName]
  , a.ssn_last4 [Last4-digitSSN]
  , a.first_name_co [Borrower2FName]
  , a.middle_name_co [Borrower2MName]
  , a.last_name_co [Borrower2LName]
  , a.ssn_last4_co [Last4-digitSSN2]
  , a.address_simple [PropertyFullStreetAddress]
  , a.city [PropertyCity]
  , a.state [PropertyState]
  , a.zip [PropertyZip]
  , f.fips_code [FIPS]
  , a.apn [APN]
  from
    vAssetsEx a
    left join vFIPS f on a.state = f.state and a.county = f.county
	where 1=1
	and a.final_disposition_date IS NULL
	
	or
	(a.final_disposition_date IS NOT NULL and final_disposition_date >= DATEADD(month, -3, getdate()))


--- FILE: ReportRunner\ReportRunner\SQL\LA_Alerts.sql ---
declare @load_id int

select @load_id = max(id) from LALoads

select  
    a.asset_id [asset_id]
    , a.name_simple
    , case when la.DFAULT_foreclosureactivity_flag = 1 then la.DFAULT_foreclosureactivity_flag else '' end [FORECLOSURE]
    , case when la.OWNCHG_ownershipchange_flag = 1 then la.OWNCHG_ownershipchange_flag else '' end [OWNERSHIP]
    , case when la.MLS_listedonmlsalert = 1 then la.MLS_listedonmlsalert else '' end [MLS LISTING]
    
    , case when la.NWLOAN_new_loans_flag = 1 then la.NWLOAN_new_loans_flag else '' end [NEW LOAN]
    , case when la.LSTCHG_lienstatus_change_flag = 1 then la.LSTCHG_lienstatus_change_flag else '' end [LIEN STATUS]
    , case when la.VALCHG_valuechange_flag = 1 then la.VALCHG_valuechange_flag else '' end  [VALUE CHAGNE]
    , case when la.TXDELQ_taxdelinquency_flag = 1 then la.TXDELQ_taxdelinquency_flag else '' end [TAX DELINQUENCY]
    , case when la.BK_bkalert = 1 then la.BK_bkalert else '' end [BANKRUPTCY]
    , case when la.LJ_liensjudgmentsalert = 1 then la.LJ_liensjudgmentsalert else '' end [LIENS/JUGEMENTS]
  from 
    LienAlert la
    join vAssetsEx a on la.asset_id = a.asset_id
  where
    la.any_alert_monitor = 1 AND la.load_id = @load_id
	and a.final_disposition_date is null

select  
    a.asset_id [asset_id]
	, a.final_disposition_date
    , a.name_simple
    , case when la.DFAULT_foreclosureactivity_flag = 1 then la.DFAULT_foreclosureactivity_flag else '' end [FORECLOSURE]
    , case when la.OWNCHG_ownershipchange_flag = 1 then la.OWNCHG_ownershipchange_flag else '' end [OWNERSHIP]
    , case when la.MLS_listedonmlsalert = 1 then la.MLS_listedonmlsalert else '' end [MLS LISTING]
    
    , case when la.NWLOAN_new_loans_flag = 1 then la.NWLOAN_new_loans_flag else '' end [NEW LOAN]
    , case when la.LSTCHG_lienstatus_change_flag = 1 then la.LSTCHG_lienstatus_change_flag else '' end [LIEN STATUS]
    , case when la.VALCHG_valuechange_flag = 1 then la.VALCHG_valuechange_flag else '' end  [VALUE CHAGNE]
    , case when la.TXDELQ_taxdelinquency_flag = 1 then la.TXDELQ_taxdelinquency_flag else '' end [TAX DELINQUENCY]
    , case when la.BK_bkalert = 1 then la.BK_bkalert else '' end [BANKRUPTCY]
    , case when la.LJ_liensjudgmentsalert = 1 then la.LJ_liensjudgmentsalert else '' end [LIENS/JUGEMENTS]
  from 
    LienAlert la
    join vAssetsEx a on la.asset_id = a.asset_id
  where
    la.any_alert_monitor = 1 AND la.load_id = @load_id
	and a.final_disposition_date is not null
  order by a.final_disposition_date


--- FILE: ReportRunner\ReportRunner\SQL\LA_Full.sql ---
declare @latest_load int
declare @latest_load_date date
select top 1 @latest_load = id,@latest_load_date=asOf from LALoads order by ASoF desc



select A.id [REF ID]
  , a.effective_date [OriginationDate]
  , a.investment_payment [OriginationLoanAmount]
  , a.first_name [Borrower1FName]
  , a.middle_name [Borrower1MName]
  , a.last_name [Borrower1LName]
  , a.ssn_last4 [Last4-digitSSN]
  
  , a.first_name_co [Borrower2FName]
  , a.middle_name_co [Borrower2MName]
  , a.last_name_co [Borrower2LName]
  , a.ssn_last4_co [Last4-digitSSN2]
  , a.address_simple [PropertyFullStreetAddress]
  , a.city [PropertyCity]
  , a.state [PropertyState]
  , a.zip [PropertyZip]
  , f.fips [FIPS]
  , a.apn [APN]
  
  from
    Assets a
    left join vFIPS f on a.state = f.state and a.county = f.county
  where
    not exists (select * from LAOut lo where lo.REF_ID = a.id and lo.load_id = @latest_load)
    or
    (a.settle_date <= dateadd(mm,12,@latest_load_date))
    OR 1=1


--- FILE: ReportRunner\ReportRunner\SQL\LA_Remove.sql ---
select 
    ref_id [REF ID], final_disposition_date
    
    
  from
    LALoads l
    join LAOut la on la.load_id = l.id
    left join vAssets a on a.asset_id = la.ref_id
  where
    l.asOf = (SELECT MAX(ASoF) from LALoads)
    AND
    (
      a.asset_id is null
      or
      a.final_disposition_date <= dateadd(mm,-3,dbo.TodayNY())
    )


--- FILE: ReportRunner\ReportRunner\SQL\LexPositionSize.sql ---
WITH terminated AS (select sum(market_value) as amount,sum(premium_recapture) as premium_recapture,account_id from vTradesEx where account_id in (7,8) and buy_sell='S' group by account_id)

select t.account,round(sum(t.market_value)- isnull(max(term.amount)+max(term.premium_recapture),0),0) as position_size_$
from vTradesEx t
left join terminated term on t.account_id = term.account_id
where t.account_id in(7,8) and buy_sell='B'
group by t.account
order by t.account


--- FILE: ReportRunner\ReportRunner\SQL\LienRecordingStatus.sql ---
drop table if exists #tmp


select 
  a.asset_id
  , MAX(case when l.unlock_lien = 1 then l.recording_date else null end) [recording_date]
  , convert(bit,SUM(case when l.unlock_lien = 1 then 1 else 0 end)) [unlock_lien_recorded]
  into #tmp
 
from
  vAssetsEx a
  join vLALiens l on l.asset_id = a.asset_id and l.latest = 1
where
  a.disposition_date is null
group by a.asset_id

select
  a.asset_id
  , a.name_simple
  , a.address_simple
  , a.state
  , z.county
  , t.recording_date
  , datediff(dd,a.effective_date,GetDate()) [days_since_closing]
  , datediff(dd,a.effective_date,t.recording_date) [closing_to_recording_days]
  , t.unlock_lien_recorded
  
  
 from
  vAssetsEx a
  join #tmp t on t.asset_id = a.asset_id
  left join ZillowHPI z on z.region_name = a.zip and region = 'ZIP'
 order by
  t.unlock_lien_recorded
  
  

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\LienStackCheck.sql ---
DROP TABLE IF EXISTS #tmpLienClashes
DROP TABLE IF EXISTS #tmpLiens
DROP TABLE IF EXISTS #tmpLiensOrdered





SELECT 
  e.asset_id
  , e.max_id
  , e.lien_position [unlock_lien_position]
  , d.lien_position [lender_lien_position]
  , d.lender_name
  , d.note
  , CASE WHEN e.final_disposition_date IS null THEN 'FALSE' ELSE 'TRUE' END [unlock_paid_off]
  , d.paid_off_at_origination [lender_paid_off]
  , e.effective_date
  INTO #tmpLienClashes
  FROM dbo.vAssetsEx e
    JOIN dbo.vDebtEx d on e.asset_id = d.asset_id
  WHERE e.lien_position = d.lien_position
      AND d.paid_off_at_origination = 0
  ORDER BY e.asset_id

SELECT COUNT(DISTINCT asset_id) [#] from #tmpLienClashes
SELECT * from #tmpLienClashes



SELECT *
   INTO #tmpLiens
FROM (
  SELECT d.asset_id 
  , d.lien_position 
  , d.lender_name
  , d.balance
  , d.paid_off_at_origination [paid_off]
  , d.note
    FROM dbo.vDebtEx d
      JOIN dbo.vAssets a on d.asset_id = a.asset_id
  
  UNION
  SELECT a.asset_id
  , a.lien_position
  , 'UNLOCK'
  , a.investment_payment [balance]
  , CASE WHEN a.final_disposition_date IS null THEN 'FALSE' ELSE 'TRUE' END [paid_off]
  , ''
    FROM dbo.vassetsex a) at 


SELECT
    t.*,
    ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY asset_id, lien_position  )   AS correctLienPostion
    INTO #tmpLiensOrdered
  FROM
    #tmpLiens t
  ORDER BY asset_id, lien_position

SELECT COUNT (DISTINCT asset_id) [#] FROM #tmpLiensOrdered t WHERE lien_position != correctLienPostion
SELECT * FROM #tmpLiensOrdered t WHERE lien_position != correctLienPostion

DROP TABLE IF EXISTS #tmpLienClashes
DROP TABLE IF EXISTS #tmpLiens
DROP TABLE IF EXISTS #tmpLiensOrdered


--- FILE: ReportRunner\ReportRunner\SQL\lien_stack.sql ---
declare @v_LatestLoadID int, @v_PreviousLoadID int
declare @v_LatestLoad_AsOfDate date 

select @v_LatestLoad_AsOfDate = asOf, @v_LatestLoadID = id from LALoads
where latest = 1

select top 1 @v_PreviousLoadID = id from LALoads
where id <> @v_LatestLoadID 
order by asOf desc

drop table if exists #tmp

select a.asset_id, address_simple,  lien_position as Badger_Lien_Position, bk_inputloanposition Lien_Alert_Position,a.effective_date, p.RECORDING_ON
into #tmp
from vAssets a
left join LienAlert l on l.asset_id = a.asset_id 
left join vPipeline p on a.asset_id = p.asset_id
where bk_inputloanposition > lien_position
and l.load_id = @v_PreviousLoadID
and final_disposition_date is null

select a.asset_id, address_simple,  lien_position as Badger_Lien_Position, bk_inputloanposition Lien_Alert_Position,a.effective_date, p.RECORDING_ON
from vAssets a
left join LienAlert l on l.asset_id = a.asset_id 
left join vPipeline p on a.asset_id = p.asset_id
where bk_inputloanposition > lien_position
and l.load_id = @v_LatestLoadID
and final_disposition_date is null
and l.asset_id not in (select asset_id from #tmp)
order by effective_date desc



select asset_id, address_simple,  Badger_Lien_Position, Lien_Alert_Position, effective_date, RECORDING_ON
from #tmp
order by effective_date desc


--- FILE: ReportRunner\ReportRunner\SQL\ManagementItems.sql ---
select 
  a.asset_id
  , a.name_simple
  
  , n.note
  , status
  , priority
  , dbo.NYTime(last_update) [last_update]
  , n.update_by
  from 
    vNotesEx n
    join vAssetsEx a on a.asset_id = n.asset_id
  where
    n.active = @active
    and latest = 1
    and priority_rank IN (1,2)
    AND (@hours_back = 0 or (datediff(hh,last_update,GetDate()) <= @hours_back))


--- FILE: ReportRunner\ReportRunner\SQL\Maxwell_Detail_Report_Sample.sql ---
declare @v_Diligence_Name varchar(255)





	select @v_Diligence_Name = max(Diligence_Name) from vMaxwellFindings where load_id = (select max(id) from MaxwellLoads) and Diligence_Name is not null



declare @v_Sample_Investment_Payment_Total float
declare @v_Sample_Count float

select @v_Sample_Investment_Payment_Total = sum(investment_payment) , @v_Sample_Count =count(*)
from Maxwell_Diligence_Master mdf
left join vMaxwellGrades grades on mdf.diligence_name= grades.diligence_name
left join vassets assets on grades.asset_id = assets.asset_id
where mdf.diligence_name = @v_Diligence_Name

select mdf.diligence_name,mdf.maxwell_transaction_id, mdf.Submitted_Date, count(*)  as [SampleSize_,], sum(assets.investment_payment) as [Investment_Payment_Total_,]
from Maxwell_Diligence_Master mdf
left join vMaxwellGrades grades on mdf.diligence_name= grades.diligence_name
left join vassets assets on grades.asset_id = assets.asset_id
where mdf.diligence_name = @v_Diligence_Name
group by mdf.diligence_name,mdf.maxwell_transaction_id, mdf.Submitted_Date, mdf.asset_count

select 'Count' as Label,count(*) as 'All_,'
	, sum((case when overall_final_loan_grade ='A' then 1 else 0 end)) as 'A_,'
	, sum((case when overall_final_loan_grade='B' then 1 else 0 end)) as 'B_,'
	, sum((case when overall_final_loan_grade='C' then 1 else 0 end)) as 'C_,'
	, sum((case when overall_final_loan_grade='D' then 1 else 0 end)) as 'D_,'
	, sum((case when (overall_final_loan_grade<> 'A' 
				  and overall_final_loan_grade<> 'B' 
				  and overall_final_loan_grade<> 'C' 
				  and overall_final_loan_grade<> 'D') then 1 else 0 end)) as 'Other_,'
from Maxwell_Diligence_Master mdf
left join vMaxwellGrades grades on mdf.diligence_name= grades.diligence_name
left join vassets assets on grades.asset_id = assets.asset_id
where mdf.diligence_name = @v_Diligence_Name
group by mdf.diligence_name, mdf.asset_count, maxwell_transaction_id, mdf.Submitted_Date
union all
select 'Investment Payment' as Label,sum(assets.investment_payment) as 'All_,'
	, sum((case when overall_final_loan_grade ='A' then 1 else 0 end)*assets.investment_payment) as 'A_,'
	, sum((case when overall_final_loan_grade='B' then 1 else 0 end)*assets.investment_payment) as 'B_,'
	, sum((case when overall_final_loan_grade='C' then 1 else 0 end)*assets.investment_payment) as 'C_,'
	, sum((case when overall_final_loan_grade='D' then 1 else 0 end)*assets.investment_payment) as 'D_,'
	, sum((case when (overall_final_loan_grade<> 'A' 
				  and overall_final_loan_grade<> 'B' 
				  and overall_final_loan_grade<> 'C' 
				  and overall_final_loan_grade<> 'D') then 1 else 0 end)*assets.investment_payment) as 'Other_,'
from Maxwell_Diligence_Master mdf
left join vMaxwellGrades grades on mdf.diligence_name= grades.diligence_name
left join vassets assets on grades.asset_id = assets.asset_id
where mdf.diligence_name = @v_Diligence_Name
group by mdf.diligence_name, mdf.asset_count, maxwell_transaction_id, mdf.Submitted_Date


Select 'Count %' as Label,count(*)/@v_Sample_Count as 'All_%'
	, sum((case when overall_final_loan_grade ='A' then 1 else 0 end))/@v_Sample_Count  as 'A_%'
	, sum((case when overall_final_loan_grade='B' then 1 else 0 end))/@v_Sample_Count  as 'B_%'
	, sum((case when overall_final_loan_grade='C' then 1 else 0 end))/@v_Sample_Count  as 'C_%'
	, sum((case when overall_final_loan_grade='D' then 1 else 0 end))/@v_Sample_Count  as 'D_%'
	, sum((case when (overall_final_loan_grade<> 'A' 
				  and overall_final_loan_grade<> 'B' 
				  and overall_final_loan_grade<> 'C' 
				  and overall_final_loan_grade<> 'D') then 1 else 0 end))/@v_Sample_Count  as 'Other_%'
from Maxwell_Diligence_Master mdf
left join vMaxwellGrades grades on mdf.diligence_name= grades.diligence_name
left join vassets assets on grades.asset_id = assets.asset_id
where mdf.diligence_name = @v_Diligence_Name
group by mdf.diligence_name, mdf.asset_count, maxwell_transaction_id, mdf.Submitted_Date
union all
select 'Investment Payment %' as Label,sum(assets.investment_payment)/@v_Sample_Investment_Payment_Total as 'All_%'
	, sum((case when overall_final_loan_grade ='A' then 1 else 0 end)*assets.investment_payment)/@v_Sample_Investment_Payment_Total as 'A_%'
	, sum((case when overall_final_loan_grade='B' then 1 else 0 end)*assets.investment_payment)/@v_Sample_Investment_Payment_Total as 'B_%'
	, sum((case when overall_final_loan_grade='C' then 1 else 0 end)*assets.investment_payment)/@v_Sample_Investment_Payment_Total as 'C_%'
	, sum((case when overall_final_loan_grade='D' then 1 else 0 end)*assets.investment_payment)/@v_Sample_Investment_Payment_Total as 'D_%'
	, sum((case when (overall_final_loan_grade<> 'A' 
				  and overall_final_loan_grade<> 'B' 
				  and overall_final_loan_grade<> 'C' 
				  and overall_final_loan_grade<> 'D') then 1 else 0 end)*assets.investment_payment)/@v_Sample_Investment_Payment_Total as 'Other_%'
from Maxwell_Diligence_Master mdf
left join vMaxwellGrades grades on mdf.diligence_name= grades.diligence_name
left join vassets assets on grades.asset_id = assets.asset_id
where mdf.diligence_name = @v_Diligence_Name
group by mdf.diligence_name, mdf.asset_count, maxwell_transaction_id, mdf.Submitted_Date

select asset_id, investment_payment, overall_final_loan_grade, finding_status, event_level, 
current_final_finding_grade, finding_category, finding_sub_category, finding_name
from vMaxwellFindings mf
where diligence_name = @v_Diligence_Name 
and load_id = (select max(load_id) from vMaxwellFindings where asset_id  = mf.asset_id)
and overall_final_loan_grade not in ('A', 'B')
and current_final_finding_grade not in ('A', 'B')
order by asset_id

select asset_id, investment_payment, overall_final_loan_grade, finding_status, event_level, 
current_final_finding_grade, finding_category, finding_sub_category, finding_name
from vMaxwellFindings mf
where diligence_name = @v_Diligence_Name 
and load_id = (select max(load_id) from vMaxwellFindings where asset_id  = mf.asset_id)
order by asset_id


--- FILE: ReportRunner\ReportRunner\SQL\maxwell_finding_detail_report.sql ---
select * from vMaxwellFindings where Diligence_Name = 'Saluda_Grade_Mar_2023' and overall_final_loan_grade ='D' and load_id = 45


--- FILE: ReportRunner\ReportRunner\SQL\MismatchedTrades.sql ---
SELECT t1.trade_id
, t1.asset_id
, t1.oface[amount]
, t1.account_id[1st_trade_acct] 
, t1.buy_sell[b/s]
, t1.counterparty_id[1st_counterparty]
, t2.account_id[2nd_trade_acct]
, t2.buy_sell[b/s2]
, t2.counterparty_id[2nd_counterparty] 
FROM dbo.[vTradesEx] t1
JOIN dbo.[vTradesEx] t2 ON t1.account_id=t2.counterparty_id
WHERE (t1.trade_id=t2.trade_id AND t1.asset_id=t2.asset_id AND t1.counterparty_ID!=t2.account_id)


--- FILE: ReportRunner\ReportRunner\SQL\MissedPayoffsDueInvestor.sql ---
select 
  s.asset_id
  , s.last_name
  , s.closing_date [hea_closing_date]
  , s.added_to_badger
  , datefromparts(year(dateadd(m,1,s.closing_date)),month(dateadd(m,1,s.closing_date)),15) [remittance_due_date]
  , p.account
  , s.cash_to_remit_to_coll_calc [cash_to_remit_to_coll_calc_|0,000.00|]
  from  
    vSettlementsEx s 
    left join vPositionsAll p on p.asset_id = s.asset_id and p.remaining_investment_payment != 0
    where added_to_badger > datefromparts(year(dateadd(m,1,s.closing_date)),month(dateadd(m,1,s.closing_date)),15) AND s.closing_date > '1/1/2022'
    and s.settlement_type != 'Foreclosure'
    and month(added_to_badger) = month(dbo.TodayNY())
    and year(added_to_badger) = year(dbo.TodayNY())


--- FILE: ReportRunner\ReportRunner\SQL\MissingApplicantMapping.sql ---
select 
  a.name_simple
  , a.asset_id
  , a.address_simple
  , a.effective_date
  , a.update_time
  , a.update_by
    from 
      vAssetsEx a
      left join AssetApplicantMap aam on aam.asset_id = a.asset_id
    where
      aam.asset_id is null
      
      
select 
  ap.applicant_id
  , ap.full_name
  , ap.email
  , ap.applicant_type
  , ap.update_time
  
    from 
      vApplicantsEx ap
    where
     ap.asset_id is null and ap.applicant_type is not null


--- FILE: ReportRunner\ReportRunner\SQL\MissingIndexes.sql ---
SELECT top 25
dm_mid.database_id AS DatabaseID,
dm_migs.avg_user_impact*(dm_migs.user_seeks+dm_migs.user_scans) Avg_Estimated_Impact,
dm_migs.last_user_seek AS Last_User_Seek,
OBJECT_NAME(dm_mid.OBJECT_ID,dm_mid.database_id) AS [TableName],
'CREATE INDEX [IX_' + OBJECT_NAME(dm_mid.OBJECT_ID,dm_mid.database_id) + '_'
+ REPLACE(REPLACE(REPLACE(ISNULL(dm_mid.equality_columns,''),', ','_'),'[',''),']','') 
+ CASE
WHEN dm_mid.equality_columns IS NOT NULL
AND dm_mid.inequality_columns IS NOT NULL THEN '_'
ELSE ''
END
+ REPLACE(REPLACE(REPLACE(ISNULL(dm_mid.inequality_columns,''),', ','_'),'[',''),']','')
+ ']'
+ ' ON ' + dm_mid.statement
+ ' (' + ISNULL (dm_mid.equality_columns,'')
+ CASE WHEN dm_mid.equality_columns IS NOT NULL AND dm_mid.inequality_columns 
IS NOT NULL THEN ',' ELSE
'' END
+ ISNULL (dm_mid.inequality_columns, '')
+ ')'
+ ISNULL (' INCLUDE (' + dm_mid.included_columns + ')', '') AS Create_Statement
FROM sys.dm_db_missing_index_groups dm_mig
INNER JOIN sys.dm_db_missing_index_group_stats dm_migs
ON dm_migs.group_handle = dm_mig.index_group_handle
INNER JOIN sys.dm_db_missing_index_details dm_mid
ON dm_mig.index_handle = dm_mid.index_handle
WHERE dm_mid.database_ID = DB_ID()
ORDER BY Avg_Estimated_Impact DESC


--- FILE: ReportRunner\ReportRunner\SQL\missing_partner_account_monday.sql ---
select u.last_name [sales], p.pipeline_id, p.max_id, p.name,p.sub_stage,investment_payment,estimated_signing, opp_source_txt, last_update
from vPipeline p left join vUsers u on u.[monday_id] = p.sales_id join MondaySubStages ms on ms.sub_stage = p.sub_stage 
where partner_account_txt is null and opp_source_txt is not null and group_name not in ('Lost') and estimated_signing >= dateadd(WEEK, -6, dbo.GetDateNY())
order by ms.[rank] desc


--- FILE: ReportRunner\ReportRunner\SQL\missing_referral_indo_max_monday.sql ---
IF OBJECT_ID(N'tempdb..#tmp') IS NOT NULL
	begin
	drop table #tmp
	end
 
select app.name as 'MAX_name', APPPARTY.APPLICATION_PARTY_TYPE as 'MAX_Party_Type', app.APPLICATION_STATE as 'MAX_Application_State', 
	PARTY."NAME" as 'MAX_Party_Name', party.email as 'MAX_Party_Email', 
		APP.MONDAY_PULSE_ID as 'Monday_Pulse_ID', p.partner_account_txt 'Monday_Partner_Account_txt',
		p.opp_source_txt 'Monday_Partner', p.asset_id as 'Monday_asset_id', p.name as 'Monday_Pipeline_Name'
	into #tmp
FROM 
	api_party PARTY, 
	API_APPLICATIONPARTY APPPARTY, 
	api_application APP,
	vPipelineEx p
WHERE PARTY.ID = APPPARTY.PARTY_ID 

	AND APPPARTY.APPLICATION_PARTY_TYPE = 'party'
	AND APP.ID = APPPARTY.APPLICATION_ID
	and p.pipeline_id = APP.MONDAY_PULSE_ID
	and party.name is null
	and p.partner_account_txt is not null
	and party.email is null
	ORDER BY app.APPLICATION_STATE, app.NAME, APPPARTY.APPLICATION_PARTY_TYPE

select MAX_name, MAX_Party_Type, MAX_Application_State, MAX_Party_Name, MAX_Party_Email, 
	#tmp.Monday_Pulse_ID, Monday_Partner_Account_txt, Monday_Partner, Monday_asset_id, Monday_Pipeline_Name, 
	CONTACT_NAME as 'Sales_Name', EMAIL as 'Sales_Email'
from #tmp,
	api_party PARTY, 
	API_APPLICATIONPARTY APPPARTY, 
	api_application APP 
	WHERE PARTY.ID = APPPARTY.PARTY_ID 
	AND APPPARTY.APPLICATION_PARTY_TYPE in  ('sales')

	AND APP.ID = APPPARTY.APPLICATION_ID
	and PARTY.DELETED_AT  is null
	and APP.MONDAY_PULSE_ID = #tmp.Monday_Pulse_ID
	order by CONTACT_NAME

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\missin_referral_in_monday_not_in_max.sql ---
IF OBJECT_ID(N'tempdb..#tmp') IS NOT NULL
	begin
	drop table #tmp
	end
 
select app.name as 'MAX_name', APPPARTY.APPLICATION_PARTY_TYPE as 'MAX_Party_Type', app.APPLICATION_STATE as 'MAX_Application_State', 
	PARTY."NAME" as 'MAX_Party_Name', party.email as 'MAX_Party_Email', 
		APP.MONDAY_PULSE_ID as 'Monday_Pulse_ID', p.partner_account_txt 'Monday_Partner_Account_txt',
		p.opp_source_txt 'Monday_Partner', p.asset_id as 'Monday_asset_id', p.name as 'Monday_Pipeline_Name'
	into #tmp
FROM 
	vPipelineEx p
	left join api_application APP on p.pipeline_id = APP.MONDAY_PULSE_ID
	left join API_APPLICATIONPARTY APPPARTY on APP.ID = APPPARTY.APPLICATION_ID
	left join api_party PARTY on PARTY.ID = APPPARTY.PARTY_ID 
WHERE PARTY.ID = APPPARTY.PARTY_ID 

	AND APPPARTY.APPLICATION_PARTY_TYPE = 'party'
	and party.email is null 
	ORDER BY app.APPLICATION_STATE, app.NAME, APPPARTY.APPLICATION_PARTY_TYPE


select distinct MAX_name, MAX_Party_Type, MAX_Application_State, MAX_Party_Name, MAX_Party_Email, 
	#tmp.Monday_Pulse_ID, Monday_Partner_Account_txt, Monday_Partner, Monday_asset_id, Monday_Pipeline_Name, 
	CONTACT_NAME as 'Unlock_Sales_Name', EMAIL as 'Unlock_Sales_Email'
from #tmp
	left join api_application APP on APP.MONDAY_PULSE_ID = #tmp.Monday_Pulse_ID
	left join API_APPLICATIONPARTY APPPARTY on APP.ID = APPPARTY.APPLICATION_ID
	left join api_party PARTY on PARTY.ID = APPPARTY.PARTY_ID 
	left join vClosingEx closing on closing.asset_id = app.EXTERNAL_ID
	WHERE PARTY.ID = APPPARTY.PARTY_ID 
	and closing.funding_date is null
	AND APPPARTY.APPLICATION_PARTY_TYPE in  ('sales')


	and APPPARTY.DELETED_AT is null
	and Monday_asset_id is not null
	and (MAX_Party_Name is not null or MAX_Party_Email is not null)
	order by CONTACT_NAME

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\MondaySupportExport.sql ---
select q.[name],p.name [customer],status,ticket_type, 'https://app2b.outreach.io/opportunities/' + converT(varchar(30),internal_id) [outreach], waiting_on,'not supported because there are 2 ID in same field - really need?' [support],p.sales,q.last_update,q.created_on,p.max_id,q.group_name from ServicingQueue q join VPipelineEx p on q.pipeline_id = p.pipeline_id join vAssets a on a.asset_id = p.asset_id where q.pipeline_id is not null


--- FILE: ReportRunner\ReportRunner\SQL\MondayTie.sql ---
SELECT
 p.pipeline_id
,p.name
,p.sub_stage
,p.estimated_signing
,p.max_id
,p.group_name
,p.loss_reason
FROM
 vPipelineEx p 
 LEFT JOIN vAssets a ON a.asset_id = p.asset_id
WHERE
 group_name IN ('Won') and a.asset_id IS NULL AND p.pipeline_id NOT IN(2455059339)



SELECT
 p.pipeline_id
,p.name
,p.sub_stage
,p.estimated_signing
,p.max_id
,p.group_name
,p.loss_reason
FROM
 vPipelineEx p 
 JOIN vAssets a ON a.asset_id = p.asset_id
WHERE
 group_name not IN ('Won') AND sub_stage not in ('Pending Escrow Disbursement','Pending Recording') 
 and a.asset_id IS not null  AND P.pipeline_id NOT IN(2455059339)


--- FILE: ReportRunner\ReportRunner\SQL\Monday_Intraday_Activity_Report.sql ---
declare @v_CurrTime datetime;
declare @v_RowCount int;
set @v_CurrTime = dbo.GetDateNY();


drop table if exists #tmp

create table #tmp (CurrentDay datetime, UpdateCount_15 int, UpdateCount_30 int, UpdateCount_60 int, UpdateCount_today int)

insert into #tmp (CurrentDay , UpdateCount_15)
select @v_CurrTime, count(*) from Pipeline where update_time > DATEADD(mi,-15,@v_CurrTime);

select @v_RowCount = count(*) from Pipeline where update_time > DATEADD(mi,-30, @v_CurrTime);
update #tmp set UpdateCount_30 = @v_RowCount;

select @v_RowCount = count(*) from Pipeline where update_time > DATEADD(mi,-60, @v_CurrTime);
update #tmp set UpdateCount_60 = @v_RowCount;

select @v_RowCount = count(*) from Pipeline where CONVERT(date, update_time) = CONVERT(date, @v_CurrTime)
update #tmp set UpdateCount_today  = @v_RowCount;

select concat('Monday sync status as of  ', format(CurrentDay ,'MM/dd/yyyy'), '   at   ', format(CurrentDay ,N'hh:mm tt')) as ' ', UpdateCount_15 as 'Updates Past 15 Minutes', UpdateCount_30 as 'Updates Past 30 Minutes', 
  UpdateCount_60 as 'Updates Past 60 Minutes', UpdateCount_today as 'Updates Today'
  from #tmp
drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\NeedAssignmentOfSecurityInstrument.sql ---
declare @asOf date
declare @start date
declare @end date

select @asOf = dbo.GetDateNY()
select @start = dateadd(d,2,DATEADD(DAY,-1,EOMONTH(@asof,-2)))
select @end = DATEADD(DAY,-1,EOMONTH(@asof,-1))
select @start = '1/1/2021'
select @end = dbo.TodayNY()

select @start [start],@end [end]

drop table if exists #tmp
drop table if exists #trades

select 
  asset_id
  , effective_date
  , case when a.state in ('FL','SC') then a.originator + ' w/Witness' else a.originator end [originator]
  , a.state
  into #tmp
  from
    vAssetsEx a
  WHERE
    a.effective_date between @start and @end
    and a.final_disposition_date is null
  
  
  
  delete t from #tmp t where exists (select asset_id from vCollatShipmentDetailEx csd where csd.collatshiptype_id = 2 and csd.docconfig_id in (3,8) and csd.asset_id = t.asset_id)

  select count(*) [#] ,min(effective_date) [earliest],max(effective_date) [latest],originator from #tmp group by originator order by count(*) desc
  
  select max(trade_id) [last_trade] ,asset_id into #trades from vTrades t where trade_id is not null and buy_sell = 'B' and is_unlock = 0 group by asset_id 
  
  select
    p.account
    , t.effective_date
    , t.asset_id
    , a.doc_custodian
    , tt.last_trade
    , t.originator
    , t.state
   from 
    #tmp t
    join vPositions p on p.asset_id = t.asset_id
    join vAccountsEx a on a.account_id = p.account_id
    left join #trades tt on tt.asset_id = p.asset_id
   
  order by t.originator, t.state, a.doc_custodian,account,effective_date
  drop table if exists #tmp
  drop table if exists #trades


--- FILE: ReportRunner\ReportRunner\SQL\NeedCreditMapping.sql ---
declare @last_run date


declare @threshold float = -10000
declare @automap bit = 1
drop table if exists #tmp


select 
  d.debt_id
  , tl.craccount_id
  , d.asset_id
  , lender_name
  , rate
  , d.balance [badger_balance_at_orination]
  , payment
  , d.lien_position
  , d.note [badger_note]
  , tl.creditor
  , tl.balance [tl_balance]
  , tl.monthly_pmt [tl_payment]
  , tl.balance-d.balance_calc [tl_balance_minus_badger_balance]
  into #tmp
  from 
    vDebtEx d join vAssets a on a.asset_id = d.asset_id 
    
    join vCRTradelinesEx tl on d.asset_id = tl.asset_id and tl.latest = 1 and (tl.acct_type in ('Mortgage') or tl.credit_loan_type in ('HomeEquityLineOfCredit')) and tl.balance != 0
    where 
      d.account_closed is null 
      and (d.cr_visible = 1 or d.cr_visible is null) 
      and (d.cr_reported = 1 or d.cr_reported is null) 
      and tl.creditor is null 
      and a.final_disposition_date is null
      and d.balance_calc != 0
      
    order by
      d.asset_id,lender_name,creditor

      
 
  
  if @automap = 1
  begin
    update d set d.craccount_id = t.craccount_id from Debt d join #tmp t on t.debt_id = d.id where tl_balance_minus_badger_balance between @threshold and 0
  end

   select * from #tmp where tl_balance_minus_badger_balance not between @threshold and 0
      
drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\NeedInsurance.sql ---
drop table if exists #tmp


select
  a.effective_date
  , a.asset_id
  , a.name_simple [name]
  , a.address_full [address]
  , i.policy_end_date
  , ic.[name] [carrier]
  , ic.rating [carrier_rating]
  , i.policy_number
  , i.coverage_amount
  , datediff(dd,GetDate(),i.policy_end_date) [days_from_expiration]
  , datediff(dd,a.effective_date,GetDate()) [days_since_origination]
  , i.unlock_insured
  into #tmp
  from
    vAssetsEx a
    left join vInsurance i on a.asset_id = i.asset_id
    left join vInsuranceCarriers ic on ic.insurancecarrier_id = i.insurancecarrier_id and ic.latest = 1
  where
    a.final_disposition_date is null
    and i.latest = 1

  
  select asset_id,effective_date,name,address, days_since_origination from #tmp where policy_end_date is null order by days_since_origination desc
  
  
  select asset_id,effective_date,name,address,policy_end_date,carrier,policy_number,carrier_rating,unlock_insured,days_from_expiration from #tmp where datediff(dd,GetDate(),policy_end_date) <= @days  order by days_from_expiration desc


--- FILE: ReportRunner\ReportRunner\SQL\NewPricing.sql ---
select 
  count(*) [count]
  , p.sub_stage
  , sum(case when a.NEW_PRICING=1 then a.REQUESTED_INVESTMENT else 0 end) [new_pricing]
  , sum(case when a.NEW_PRICING=0 then a.REQUESTED_INVESTMENT else 0 end) [old_pricing]
  from 
    vPipelineEx p
    left join vAPI_APPLICATION a on a.EXTERNAL_ID = p.max_id
    left join vPositions pos on pos.asset_id = p.asset_id
    left join MondaySubStages m on m.sub_stage = p.sub_stage
  where
    p.sub_stage not in ('Closed Lost')
    and p.group_name not in ('Lost','Paused')
    and (pos.account in ('UPS') OR pos.ACCOUNT IS NULL)
  group by
    p.sub_stage
    , m.rank
  order by 
    m.[rank]


--- FILE: ReportRunner\ReportRunner\SQL\new_referral_partner_in_pipeline.sql ---
select pipe.Max_id as 'Max ID', pipe.estimated_signing  as 'Estimated Close', pipe.APPLICATION_STATE as 'Application State', pipe.name as 'Applicant',
	pipe.opp_source_txt as 'Referral Contact', pipe.partner_account_txt as 'Referral Name', pipe.opp_source_email as 'Referral EMail',
	pipe.sales_first_name, sales_last_name
	FROM vPipeline pipe
where pipe.opp_source_email not in (select email_full from ReferralCommissionInfo)
and pipe.APPLICATION_STATE <> 'closed-lost'
and pipe.estimated_signing between DATEADD(MONTH,-1, dbo.TodayNY()) and DATEADD(week,2, dbo.TodayNY())


--- FILE: ReportRunner\ReportRunner\SQL\NightlyReport[Conflict].sql ---
declare @date smalldatetime
	declare @businessdate_id int
	exec GetControlDate @date=@date OUT
	select @businessdate_id=id from BusinessDates where business_date = @date
	select sum(total) from Checks where businessdate_id = @businessdate_id


select sum(convert(decimal(18,2),(cast(datediff(n, clock_in, clock_out)as float)/60))*rate)
  from 
  TimeCards t
  join Employees e on t.employee_id = e.id
  where businessdate_id = @businessdate_id


--- FILE: ReportRunner\ReportRunner\SQL\NonPaidOffAccounts.sql ---
select a.asset_id,a.name_simple,a.address_full,a.effective_date,d.lender_name [badger_lender],d.cr_creditor,d.balance_calc [badger_balance],d.cr_balance [cr_balance],d.cr_asof
  from 
    vDebtEx d 
  join vAssetsEx a on a.asset_id = d.asset_id
  where
    a.final_disposition_date is null
    and d.balance_calc = 0
    and d.cr_balance != 0


--- FILE: ReportRunner\ReportRunner\SQL\OriginatedDeals.sql ---
select
distinct
  a.asset_id
  , a.effective_date
  , app.first_name
  , app.last_name
  , app.full_name
  , a.name_simple
  
  
  
  
  , case when app.mailing_address_1 is not null then 'MAILING' else 'HEI ADDRESS' END [ADDRESS TYPE]
  , case when app.mailing_address_1 is not null then app.mailing_address_1 else address_1 end [address_1]
  , case when app.mailing_address_1 is not null then app.mailing_address_2 else address_2 end [address_2]
  , case when app.mailing_address_1 is not null then app.mailing_city else city end [city]
  , case when app.mailing_address_1 is not null then app.mailing_state else state end [state]
  , case when app.mailing_address_1 is not null then app.mailing_zip else zip end [zip]
  , app.email
  , app.phone
  from
    vAssetsEx a
    left join vApplicantsEx app on app.asset_id = a.asset_id and applicanttype_id = 1

  
    


order by a.effective_date desc


--- FILE: ReportRunner\ReportRunner\SQL\OwnerOccupied.sql ---
select 
  a.asset_id
  , a.name_simple
  , a.address_simple
  , ot.[name] [badger]
  , l.bk_owneroccupied
  from 
    vLienAlert l
    join vAssetsEx a on l.asset_id = a.asset_id
    join OccupancyTypes ot on ot.id = a.occupancytype_id
  where 
    l.bk_owneroccupied != ot.is_oo and l.latest =1


--- FILE: ReportRunner\ReportRunner\SQL\PaidOffJournals.sql ---
drop table if exists #tmp

select
  a.name_simple
  , a.address_simple
  , s.cash_to_remit_to_coll_calc
  , DATEDIFF(D,a.effective_date,A.FINAL_DISPOSITION_DATE) [age_days]
  , a.final_disposition_date
  , p.account
  , p.wavg_px [purchase_price]
  , prod.asset_premium_recapture_eligible
  , acct.account_premium_recapture_eligible
  
  
  , s.note_last
  , null [_]
  , a.asset_id
  , a.investment_payment [oface]
  , p.account_id
  , 'S' [buy_sell]
  , 0 [counterparty_id]
  
  
  , datefromparts(year(dateadd(month,1,a.final_disposition_date)),month(dateadd(month,1,a.final_disposition_date)),15) [trade_date]
  , dateadd(d,-1,datefromparts(year(dateadd(month,1,a.final_disposition_date)),month(dateadd(month,1,a.final_disposition_date)),1)) [settle_date]
  
  , convert(float,null) [price]

  into #tmp
from
  vAssetsEx a
  join vPositions p on p.asset_id = a.asset_id
  join vSettlementsEx s on s.asset_id = a.asset_id
  left join vProducts prod on prod.product_id = a.product_id
  left join vAccounts acct on acct.account_id = p.account_id
  where
    a.final_disposition_date is not null
    and p.is_unlock = 0
    and a.final_disposition_date <= DATEADD(DAY,0,EOMONTH(GetDate(),-1))
    
    

  update #tmp set price = ((cash_to_remit_to_coll_calc)/oface)*100.0
  
   
  select * from #tmp order by account, final_disposition_date
  
drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\PendingOnboard.sql ---
drop table if exists #tmp 

select 
  t.asset_id
  , a.name_simple [name]
  , count(*) [total_tasks]
  , sum(convert(int,t.task_complete)) [completed]
  , count(*)-sum(convert(int,t.task_complete)) [not_complete]
  , a.sign_date
  , datediff(dd,a.sign_date,GetDate()) [days_elapsed]
  , ts.eta_days [eta_(days)]
  , datediff(dd,a.sign_date,GetDate())-ts.eta_days [past_eta_(days)]
 
  into #tmp
  from 
    vTasks t
    join Assets a on a.id = t.asset_id
    join TaskSets ts on ts.id = t.taskset_id
  where
    t.taskset_id = @taskset_id
    and t.latest = 1  
    
  group by
    t.asset_id
    , a.sign_date
    , a.name_simple
    , ts.eta_days
  order by name desc
    
select * from #tmp

select 
  t.asset_id
  , tp.name
  , tt.[TYPE] task_type
  , tc.name [task_name]
  , ts.status

  from
    #tmp tp
    join vTasks t on t.asset_id = tp.asset_id and t.taskset_id = @taskset_id
    join TaskConfig tc on t.taskconfig_id = tc.id
    join TaskStatus ts on t.taskstatus_id = ts.id
    join TaskTypes tt on tt.id = t.tasktype_id
    where
      t.task_complete = 0
      and t.latest = 1
    order by name desc

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\PendingSettlementRequests.sql ---
drop table if exists #tmp

select 
  sr.asset_id
  ,sr.statement_void_after
  ,sr.account
  ,sr.statement_date
  ,sr.settlement_type
  ,sr.settlementtype_id
  ,sr.settlement_reason
  ,convert(date,format(sr.statement_date,'M/1/yyyy')) [statement_month]
  ,a.unlock_share_estimate
  ,a.final_disposition_date
  ,case when a.final_disposition_date is null then 0 else 1 end [terminated]
  into #tmp from vSettlementRequestsEx sr
  join vAssetsEx a on sr.asset_id = a.asset_id
  where sr.latest=1
    
  select count(*) [# PENDING REQUESTS], sum(unlock_share_estimate) [unlock_share_estimate_|0,000|] from #tmp where statement_void_after >= dbo.TodayNY() and terminated=0
  select count(*) [#], sum(unlock_share_estimate) [unlock_share_estimate_|0,000|], account from #tmp where statement_void_after >= dbo.TodayNY() and terminated=0 group by account
  
  select statement_month, sum(monthly_requests) [# FINAL REQUESTS], sum(monthly_buyouts) [# BUYOUTS], sum(monthly_home_sales) [# HOME SALES], sum(unlock_share_estimate) [unlock_share_estimate_|0,000|], sum(payoffs) [# SETTLEMENTS], sum(proceeds) [proceeds_|0,000|], format((sum(t.payoffs)*1.0)/(sum(t.monthly_requests)*1.0),'P') [% SETTLED] from
  (select statement_month
  ,count(*) [monthly_requests]
  ,sum(case when settlementtype_id=1 then 1 else 0 end) [MONTHLY_BUYOUTS]
  ,sum(case when settlementtype_id=2 then 1 else 0 end) [MONTHLY_HOME_SALES]
  ,sum(unlock_share_estimate) [unlock_share_estimate]
  ,sum(case when terminated=1 then 1 else 0 end)[payoffs]
  ,case when terminated=1 then sum(unlock_share_estimate) else 0 end [proceeds]
  from #tmp 
  group by statement_month,terminated 
  ) t
  group by statement_month order by statement_month desc
  
  select count(*) [#], sum(unlock_share_estimate) [unlock_share_estimate_|0,000|], settlement_reason from #tmp where statement_void_after >= dbo.TodayNY() and terminated=0 group by settlement_reason
  
  select asset_id
  ,statement_void_after [VOID_AFTER]
  ,settlement_type
  ,settlement_reason
  ,account
  ,statement_date
  ,unlock_share_estimate
  ,final_disposition_date
  from #tmp order by account, final_disposition_date asc, statement_date asc
 
 drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\PendingSubmitUSB.sql ---
SELECT 
  f.asset_id
  , f.customer_pipeline_label
  , f.investment_payment 
  , f.effective_date
  , p.sub_stage
  , f.funding_date
  , f.originated
  
  , dbo.BizDayDiff(f.effective_date,dbo.TodayNY()) [days_since_signing]
  , last_ship [ship_date_to_usb]
  
  , c.cert_status
  
  FROM 
    vFundings f
    left join vCollatInv c on c.asset_id = f.asset_id and c.latest = 1
    left join (select max(ship_date) [last_ship] ,asset_id from vCollatShipmentDetailEx csd where csd.COLLATSHIPTYPE_ID=1 group by asset_id) s on s.asset_id = f.asset_id
    left join vPipeline p on p.PIPELINE_ID = f.PIPELINE_ID
  where 
  funding_date is not null
  and f.originated = 1
  and
  last_ship is null and cert_status is null and dbo.BizDayDiff(f.effective_date,dbo.TodayNY()) > @days_since_signing


--- FILE: ReportRunner\ReportRunner\SQL\PendingUSBCollat.sql ---
drop table if exists #tmp

SELECT
  a.asset_id
  , a.name_simple
  , a.address_simple
  , a.investment_payment
  , a.investment_payment*1.06 [total_proceeds]
  , a.effective_date
  , a.added_to_badger
  , dbo.BizDayDiff(a.effective_date,dbo.TodayNY()) [biz_days_since_signing]
  , cs.ship_date
  , dbo.BizDayDiff(cs.ship_date,dbo.TodayNY()) [biz_days_since_sending_to_usb]
  , cs.[type]
  , case when dbo.BizDayDiff(cs.ship_date,dbo.TodayNY()) is not null then 'SHIPPED' when [type] = 'DIGITAL' then 'PENDING SHIPPING' ELSE 'NOT SHIPPED' END [ship_status]
  

  into #tmp
  FROM 
    vAssetsEx a
    left join vCollatInv i on a.asset_id = i.asset_id and latest = 1
    left join vCollatShipmentsSingleEx cs on cs.asset_id = a.asset_id
  where
    i.asset_id is null
    AND (CS.type = 'Digital' or cs.type is null)
   
   
   
   

delete t from #tmp t where exists (select * from vTrades tr where tr.asset_id = t.asset_id and tr.buy_sell = 'S' and tr.is_unlock = 1)


select concat('Last Collateral Load   ', format(max(update_time),'MM/dd/yyyy'), '   at   ', format(max(update_time),N'hh:mm tt')) as 'Last Collateral Load' from CollatLoads


select count(*) [#],sum(investment_payment) [investment_payment_$],sum(total_proceeds) [total_proceeds_$], null [_], null [__],sum(case when biz_days_since_sending_to_usb >2 then total_proceeds else 0 end) [total_proceeds_past_sla_$] from #tmp

select count(*) [#],sum(investment_payment) [investment_payment_$],sum(total_proceeds) [total_proceeds_$],ship_status from #tmp GROUP BY ship_status

select count(*) [#],biz_days_since_sending_to_usb,sum(investment_payment) [investment_payment_$],sum(total_proceeds) [total_proceeds_$] from #tmp group by biz_days_since_sending_to_usb order by biz_days_since_sending_to_usb asc


select 
  asset_id
  , name_simple
  , address_simple
  , investment_payment [investment_payment_$]
  , total_proceeds [total_proceeds_$]
  , effective_date
  , added_to_badger
  , biz_days_since_signing
  , ship_date
  , ship_status
  , biz_days_since_sending_to_usb
  from #tmp
  order by ship_status,biz_days_since_sending_to_usb

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\Pending_Wires.sql ---
select sum(investment_payment) as 'investment_payment', sum(net_wire_amt) as 'net_wire_amt'
from vFundings f 
where f.funding_date is null and f.effective_date = dbo.TodayNY()
group by effective_Date

select asset_id, customer_pipeline_label,effective_Date,investment_payment,net_wire_amt,note 
from vFundings f 
where f.funding_date is null and f.effective_date = dbo.TodayNY()


--- FILE: ReportRunner\ReportRunner\SQL\PipelinePricingSummary.sql ---
drop table if exists #tmp
drop table if exists #final

select  
  m.rank [substage_rank]
  , p.max_id

  , p.sub_stage
  , (case when p.investment_payment is not null then p.investment_payment else p.investment_payment_requested end) as investment_payment 
  , p.estimated_signing
  , a.application_id
  , ass.msa_name
  , ass.state
  , ass.credit_score
  , at.lien_position+1 [lien_position]
  , a.ANNUALIZED_COST_LIMIT_CALC_VERSION
  into #tmp
from 
  vPipeline p 
  join vAPI_Application a on p.max_id = a.EXTERNAL_ID
  left join  MondaySubStages m on m.sub_stage = p.sub_stage
  left join vAssetsEx ass on ass.max_id = p.max_id
  left join (select application_id,sum(case when mortgage_debt = 1 then unpaid_balance_amount-payoff_amount else 0 end) [debt_calc],sum(case when mortgage_debt = 1 and (unpaid_balance_amount-payoff_amount)>0 then 1 else 0 end) [lien_position] from api_tradeline WHERE DELETED_AT IS NULL AND MORTGAGE_FOR_ID IS NOT NULL group by application_id) at on at.application_id = a.application_id
  where 
    p.sub_stage not in ('Closed Lost','Closed Won') 
    and p.group_name not in ('Lost','Won') 
	and estimated_signing is not null
	and a.APPLICATION_STATE not in ('Pending App Submit', 'Pending App Submit', 'Pending Doc Upload')


 select
  substage_rank [rank_|0|]
  , count(*) [#]
  
  , sub_stage
  , sum(o.annualized_cost_limit * case when annualized_cost_limit is null then 0 else investment_payment end)/sum(case when annualized_cost_limit is null then 0 else investment_payment end) [avg_acl_|0.000%|]
  , sum(o.exchange_rate * case when (o.exchange_rate is null or o.exchange_rate = 0) then 0 else investment_payment end)/sum(case when (o.exchange_rate is null or o.exchange_rate = 0) then 0 else investment_payment end) [avg_exch_rate_|0.000|]
  , sum(investment_payment) [total_investment_payment_$]
  , sum(o.INPUT_FICO * case when o.INPUT_FICO is null then 0 else investment_payment end)/sum(case when o.INPUT_FICO is null then 0 else investment_payment end) [avg_fico_|0.000|]
  , sum(o.total_home_finance * case when o.total_home_finance is null then 0 else investment_payment end)/sum(case when o.total_home_finance is null then 0 else investment_payment end) [avg_THF_|0.000|]
  , sum(o.thf_limit * case when o.thf_limit is null then 0 else investment_payment end)/sum(case when o.thf_limit is null then 0 else investment_payment end) [avg_THFL_|0.000|]
  into #final
    from 
      #tmp t
    left join vAPI_OFFER o on o.APPLICATION_ID = t.application_id
	where investment_payment is not null 
	and investment_payment <> 0
    group by 
      sub_stage, substage_rank
  ORDER by
    substage_rank desc
    
   
    select sum([#]) [#], sum([avg_acl_|0.000%|]*[total_investment_payment_$])/sum([total_investment_payment_$]) [avg_acl_|0.000%|],sum([avg_exch_rate_|0.000|]*[total_investment_payment_$])/sum([total_investment_payment_$]) [avg_exchange_rate|0.000|],sum([total_investment_payment_$]) [total_investment_payment_$] from #final t where  [rank_|0|]>= 12
    select sum([#]) [#], sum([avg_acl_|0.000%|]*[total_investment_payment_$])/sum([total_investment_payment_$]) [avg_acl_|0.000%|],sum([avg_exch_rate_|0.000|]*[total_investment_payment_$])/sum([total_investment_payment_$]) [avg_exchange_rate|0.000|],sum([total_investment_payment_$]) [total_investment_payment_$] from #final t where  [rank_|0|]>= 6
    
    select * from #final order by [rank_|0|] desc
  
 select estimated_signing,count(*) [#], 
	sum(o.annualized_cost_limit*investment_payment)/sum(investment_payment) [wavg_cost_limit_|0.00%|],
	sum(exchange_rate*investment_payment) [wavg_exchange_rate_|0.00|],  
	sum(investment_payment) [investment_payment_$] 
 from #tmp t left join API_OFFER o on o.APPLICATION_ID = t.application_id  
 where  substage_rank >= 12 
 group by estimated_signing order by estimated_signing
 

 select t.*,total_home_finance,thf_limit,input_debt,input_home_value,annualized_cost_limit,exchange_rate [exchange_rate],input_fico 
	from #tmp t 
	left join vAPI_OFFER o on o.APPLICATION_ID = t.application_id 


	order by substage_rank desc 

drop table if exists #tmp
drop table if exists #final


--- FILE: ReportRunner\ReportRunner\SQL\PortfolioExceptions.sql ---
drop table if exists #tmp

declare @total_port float
declare @total_except float
select @total_port=sum(p.orig_buy_investment_payment) from vPositionsAll p where p.account_id = @account_id
     
select 
  pe.asset_id
  , pe.name_simple
  , pe.investment_payment
  , pe.exception_type
  , pe.exception_desc
  , pe.bounds_low
  , pe.bounds_high
  , pe.value
  , pe.guideline_label
  into #tmp
    from 
      vPortfolioExceptions pe
      join vGuidelines g on g.guideline_id = pe.guideline_id
      join vAccounts a on a.account_id = pe.account_id
    where 
      pe.account_id = @account_id
      and g.guideline_id = a.guideline_id_latest
    order by
      pe.name_simple

  select @total_except=sum(investment_payment) from #tmp


  select 
    @total_port [total_investment_pmt_$]
    , sum(investment_payment) [exception_bucket_$]
    , sum(investment_payment)/@total_port [exception_pct_|0.00%|]
  from
    #tmp
    
  select
    t.exception_desc
    , sum(t.investment_payment) [investment_pmt_$]
    , sum(t.investment_payment)/@total_except [pct_of_exception_bucket_|0.00%|]
    from 
      #tmp t
    group by t.exception_desc
    order by sum(t.investment_payment) desc
      
select   
    pe.asset_id
  , pe.name_simple
  , pe.investment_payment
  , pe.exception_type
  , pe.exception_desc
  , pe.bounds_low
  , pe.bounds_high
  , pe.value
  , pe.guideline_label 
  , pe.investment_payment/@total_except [pct_of_exception_bucket_|0.00%|]
  from #tmp pe
  order by investment_payment desc
    
drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\PostCloseIssues.sql ---
select 
  a.asset_id
  , a.effective_date
  , i.check_label
  , a.name_simple
  
  , n.note
  , status
  , priority
  , dbo.NYTime(last_update) [last_update]
  , n.update_by
  from 
    vNotesEx n
    join vAssetsEx a on a.asset_id = n.asset_id
    join vForeignIds fi on fi.foreignid_id = n.foreignid_id 
    join vIntegrityChecksEx i on i.integritycheck_id = fi.foreign_id 
  where
    n.active = @active
    and latest = 1
    and n.note_foreignidtype_id = 3 
    AND i.integritychecktype_id = 5
    
    AND (@hours_back = 0 or (datediff(hh,last_update,GetDate()) <= @hours_back))
    
  order by last_update desc


--- FILE: ReportRunner\ReportRunner\SQL\PostCreditLoad.sql ---
drop table if exists #tmp

declare @last_credit date
select @last_credit = c.latest from (select max(asOf) [latest] from vCreditFiles where latest_api = 1 having count(*)>1000) c

select a.account 
, a.asset_id
, a.max_id
, ctl.creditfile_id
, ctl.asOf [credit_run_date]
, ctl.date_opened
, ctl.date_last_activity
, ctl.date_reported
, year(a.effective_date) [origination_year]
, a.effective_date
, a.folder_name_ups
, ctl.balance
, a.last_name
, a.full_name
, a.address_full
, ctl.open_close [account_status]
, ctl.creditor [creditor_name]
, ctl.status [pay_hist_desc]
, ctl.paystring_full [paystring]
, left(ctl.paystring_full,1) [paystring_latest]
, CASE WHEN left(ctl.paystring_full,1) = '4' THEN 
    CASE WHEN PATINDEX('%[^4]%',ctl.paystring_full) = 0 THEN LEn(ctl.paystring_full) ELSE PATINDEX('%[^4]%',ctl.paystring_full)-1 END
    ELSE null 
  END [120+ length]


into #tmp from vAssetsPositionEx a 
join vCRTradelinesEx ctl on a.asset_id = ctl.asset_id and ctl.latest = 1 and a.asset_id = ctl.asset_id and (ctl.debt_type='Mortgage'
or ctl.credit_loan_type in ('Secured','HomeEquityLineOfCredit','HomeEquity','ConventionalRealEstateMortgage','CreditLineSecured'))
join vDebt d on ctl.craccount_id = d.craccount_id and d.asset_id = ctl.asset_id
where ctl.balance <> 0 and a.final_disposition_date is null

SELECT * FROM  #tmp 
ORDER BY CASE 
     WHEN [paystring_latest] = '4' THEN 1
     WHEN [paystring_latest] = '3' THEN 2
     WHEN [paystring_latest] = '2' THEN 3
     WHEN [paystring_latest] = '1' THEN 4
     WHEN [paystring_latest] = 'C' THEN 5
     WHEN [paystring_latest] = null THEN 6
     ELSE 7
     END ASC, [120+ length] desc
     
select asset_id,max(max_id) [max_id],max(creditfile_id) [creditfile_id],max(credit_run_date) [credit_run_date]
  from #tmp 
    group by asset_id 
    having max(credit_run_date) != @last_credit


--- FILE: ReportRunner\ReportRunner\SQL\potential_new_pre_paid_expenses.sql ---
select expense.APPLICATION_ID, expense.name, expense.paid_to, pipe.Max_id, pipe.applicant_name, pipe.APPLICATION_STATE
from api_expense expense 
left join vPipeline pipe on pipe.application_id = expense.APPLICATION_ID 
where expense.name not in 
	(select MaxExpenseName from ClosingExpenseMap where IsPrePaidExpense =1) 
	and (expense.name like '%appraisal%' or expense.name like '%1004%' or expense.name like '%inspection%' )
	and pipe.APPLICATION_STATE  <> 'closed-lost'
	and expense.name <> 'Home Inspection' 
	and expense.name <> 'Inspection'


--- FILE: ReportRunner\ReportRunner\SQL\ReadyToFund.sql ---
SELECT 
  p.name
  , p.sub_stage
  , p.investment_payment [investment_payment_$]
  , p.estimated_signing
  , p.exception 
  into #tmp 
  from 
    vPipeline p 
    left join vClosing c on c.pipeline_id = p.pipeline_id 
  where 
    c.asset_id IS NULL 
    AND p.sub_stage in ('Pending Wire','Pending Signature')
    AND p.group_name IN ('Active Pipeline') 
    
    select 
      count(*) [#]
      , sum([investment_payment_$]) [investment_payment_$] from #tmp 
    
    select * from #tmp 
    
    
    drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\RollingCreditIssues.sql ---
select
  l.asset_id
  , a.name_simple
  , a.age
  , l.asof [latest_asof]
  , p.asof [prior_asof]
  
  , i.credit_score_calc [credit_score_origination_|0|]
  , l.credit_score_calc [credit_score_latest_|0|]
  , p.credit_score_calc [credit_score_3mo_|0|]
  , l.credit_score_calc-p.credit_score_calc [credit_score_3mo_delta_|0|]
  from 
    vCreditScoreAsset l
    join vCreditScoreAsset p on p.asset_id = l.asset_id and datediff(m,p.asOf,l.asOf) = @MONTHS_BACK 
    join vAssetsEx a on a.asset_id = l.asset_id
    left join vCreditScoreAsset i on p.asset_id = i.asset_id and i.initial = 1
  where
    l.latest = 1
    and (l.credit_score_calc-p.credit_score_calc) < @THRESHOLD
    ORDER BY (l.credit_score_calc-p.credit_score_calc) ASC


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_DealTie.sql ---
declare @tape_id int, @account_id int
select @tape_id = tape_id,@account_id = account_id from vTapesEx t where t.account = @account and t.latest_tapetype = 1 and tapetype_id = 2

drop table if exists #a
drop table if exists #tmp

select asset_id,sum(ending_upb) [ending_upb],max(tape_cutoff) [tape_cutoff] into #a from vTapeDetailEx td where td.tape_id = @tape_id group by asset_id


select 
  a.asset_id
  , ass.loan_id
  , sum(t.net_oface) [trade_position_$]
  , max(settle_date) [last_trade_sd]
  , a.ending_upb [ending_upb] 
  , a.ending_upb-sum(t.net_oface) [delta]
  into #tmp
from 
  vTradesEx t 
  join #a a on a.asset_id = t.asset_id
  join vAssets ass on ass.asset_id = t.asset_id
where   
  t.settle_date <= a.tape_cutoff
  and t.account_id = @account_id
  group by 
    a.asset_id
    , ass.loan_id
    , a.ending_upb

select * from #tmp where delta != 0


drop table if exists #a
drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_ExtraTrades.sql ---
declare @last_remit int, @account_id int

select @account_id = account_id from vAccounts a where a.name_short = @deal

drop table if exists #tmp

select @deal [deal],t.settle_date,a.asset_id,a.loan_id,a.originator,t.oface [oface]
into #tmp
  from 
    vTradesEx t
    join vAssets a on a.asset_id = t.asset_id
  where 
    t.account_id = @account_id
    and not exists (select * from vTapeDetailEx td where td.asset_id = t.asset_id and td.tapetype_id = 2 and td.latest_tapetype_month = 1 and td.account_id = t.account_id)
    and t.ticket_type = 'TT'

select * from #tmp order by settle_date


drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_MissingAssets.sql ---
drop table if exists #tmp

declare @asof date
select @asof = EOMONTH(gETdATE(),-1)

select distinct loan_id,d.status,d.last_update,sg_deal,d.request_type,d.reimbursement_date,d.group_name into #tmp from vDrawsEx d where d.asset_id is null and status is not null and d.sg_deal = @deal AND LAST_UPDATE <= @asof AND GROUP_NAME NOT IN ('Rejected') order by last_update desc

select distinct loan_id,min(last_update) [earliest_update],max(last_update) [latest_update] from #tmp group by loan_id

select * from #tmp

drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_MissingMappings_DELETE.sql ---
drop table if exists #missing

create table #missing
(
  count int
  , field varchar(30)
  , missing_map varchar(100)
)

insert into #missing (count,field,missing_map) select count(*),'property_type',td.property_type from vTapeDetail td left join Maps m on m.db_field = 'property_type' and m.map_from = td.property_type where m.map_from is null and td.property_type is not null and td.asset_latest = 1 group by td.property_type
insert into #missing (count,field,missing_map) select count(*),'product_type',td.product_type from vTapeDetail td left join Maps m on m.db_field = 'product_type' and m.map_from = td.product_type where m.map_from is null and td.product_type is not null and td.asset_latest = 1 group by td.product_type
insert into #missing (count,field,missing_map) select count(*),'loan_purpose',td.loan_purpose from vTapeDetail td left join Maps m on m.db_field = 'loan_purpose' and m.map_from = td.loan_purpose where m.map_from is null and td.loan_purpose is not null and td.asset_latest = 1 group by td.loan_purpose

select * from #missing order by field desc,count desc,missing_map
select distinct db_field,map_to from Maps m where m.db_field in('property_type','product_type','loan_purpose') and m.map_to is not null order by m.db_field,map_to

drop table if exists #missing


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_MissingRemits.sql ---
drop table if exists #tmp


select t.account_id,a.name [account_name],count(*) [count],datediff(m,min(t.cutoff_date),max(t.cutoff_date))+1 [should_have] into #tmp from vTapesEx t join vAccounts a on a.account_id = t.account_id where t.latest_tapetype_month = 1 and t.tapetype_id = 2 and a.accounttype_id = 1 group by t.account_id,a.name

select account,cutoff_date,[should_have]-[count] [num_missing] from vTapesEx t join #tmp tmp on tmp.account_id = t.account_id join vAccounts a on a.account_id = t.account_id where t.latest_tapetype_month = 1 and t.tapetype_id = 2 and a.accounttype_id = 1 and should_have != count  order by account,cutoff_date

drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_MissingTrades.sql ---
declare @last_remit int, @account_id int

select @account_id = account_id from vAccounts a where a.name_short = @deal

drop table if exists #tmp

select @deal [deal],td.tape_cutoff,td.asset_id,td.loan_id,a.originator,td.purchased_upb
into #tmp
  from 
    vTapeDetailEx td 
    join vAssets a on a.asset_id = td.asset_id
  where 
    td.tapetype_id = 2 
    and td.latest_tapetype_month = 1 
    and td.account_id = @account_id
    
    and not exists (select * from vTrades t where t.asset_id = td.asset_id and t.oface = td.purchased_upb and t.account_id = @account_id and t.buy_sell = 'B')
    
    and td.purchased_upb != 0
  order by
    td.tape_cutoff

select tape_cutoff,count(*) [missing_trades] from #tmp group by tape_cutoff

select * from #tmp order by deal,tape_cutoff

drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SALUDA_RemitCompare.sql ---
drop table if exists #latest_loan_schedule
drop table if exists #remit
drop table if exists #summary
drop table if exists #loan_schedule

declare @account_id int
select @account_id = account_id from vAccounts a where a.name = @deal

declare @latest_remit_tape_id int
select @latest_remit_tape_id = id from Tapes t where t.account_id = @account_id and t.tapetype_id = 2 and t.latest_tapetype = 1

select 
  asset_id
  , td.origination_date
  , td.original_maturity_date
  , td.fico
  , td.ltarv
  into #remit
  from 
    TapeDetail td
    where td.tape_id = @latest_remit_tape_id


select 
  asset_id
  , max(t.tape_id) [latest_tape_id_loan_schedule] 
  into #latest_loan_schedule
  from 
    vTapes t 
  join vTapeDetail td on td.tape_id = t.tape_id
  where
    t.tapetype_id = 3
  group by 
    td.asset_id
    
select 
  td.asset_id
  , td.origination_date
  , td.original_maturity_date
  , td.fico
  , td.ltarv
  , latest_tape_id_loan_schedule
  into #loan_schedule
  from 
    TapeDetail td
    join #latest_loan_schedule l on l.asset_id = td.asset_id and l.latest_tape_id_loan_schedule = td.tape_id
    
create table #summary
  (
    asset_id bigint
    , loan_id varchar(30)
    , field varchar(30)
    , remittance_date date
    , corrected_date date
    , remittance_value float
    , corrected_value float
    , corrected_tape_id int
    , loan_schedule_file_name varchar(150)
  )
  
insert into #summary (asset_id,field,remittance_date,corrected_date,corrected_tape_id) select r.asset_id,'Origination Date',r.origination_date,l.origination_date,latest_tape_id_loan_schedule from #remit r join #loan_schedule l on l.asset_id = r.asset_id and l.origination_date != r.origination_date
insert into #summary (asset_id,field,remittance_date,corrected_date,corrected_tape_id) select r.asset_id,'Original Maturity Date',r.original_maturity_date,l.original_maturity_date,latest_tape_id_loan_schedule from #remit r join #loan_schedule l on l.asset_id = r.asset_id and l.original_maturity_date != r.original_maturity_date
insert into #summary (asset_id,field,remittance_value,corrected_value,corrected_tape_id) select r.asset_id,'FICO',r.fico,l.fico,latest_tape_id_loan_schedule from #remit r join #loan_schedule l on l.asset_id = r.asset_id and isnull(l.fico,0) != isnull(r.fico,0)
insert into #summary (asset_id,field,remittance_value,corrected_value,corrected_tape_id) select r.asset_id,'LTARV',r.ltarv,l.ltarv,latest_tape_id_loan_schedule from #remit r join #loan_schedule l on l.asset_id = r.asset_id and abs(isnull(l.ltarv,0)-isnull(r.ltarv,0))>.05


update s set loan_id = a.loan_id from #summary s join vAssets a on a.asset_id = s.asset_id
update s set loan_schedule_file_name = t.[filename] from #summary s join vTapes t on t.tape_id = s.corrected_tape_id

select loan_id,field,remittance_date,corrected_date,remittance_value,corrected_value,loan_schedule_file_name from #summary order by field

drop table if exists #latest_loan_schedule
drop table if exists #remit
drop table if exists #summary
drop table if exists #loan_schedule


--- FILE: ReportRunner\ReportRunner\SQL\SendtoUSB.sql ---
DROP TABLE IF EXISTS #TMP 

select
  a.asset_id
  , a.name_simple
  , a.investment_payment
  , a.address_simple
  , a.state
  , a.effective_date
  INTO #TMP
    from
  vAssetsEx a
  where 
    not exists (select * from vCollatInv ci where ci.asset_id = a.asset_id)
    and
    not exists (select * from vCollatShipmentMap csm where csm.asset_id = a.asset_id)
  
  
  select
    count(*) [deal_count]
    , sum(t.investment_payment) [investment_payment]
    , sum(t.investment_payment*1.06) [approx_proceeds_$]
    , sum(t.investment_payment*.06) [approx_revenue_$]
    , sum(t.investment_payment)/count(*) [avg_deal_size_$]
    , min(t.effective_date) [origination_earliest]
    , max(t.effective_date) [origination_latest]
  from
    #tmp t
 
 select
  a.asset_id
  , a.name_simple
  , a.investment_payment [investment_payment_$]
  , a.address_simple
  , a.state
  , a.effective_date 
    from 
    #tmp a
   order by effective_date ASC
 
 drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SettledAssetsInPortfolio.sql ---
select pos.account, pos.asset_id, pos.last_trade, pos.last_settle, pos.remaining_investment_payment, closing_date, settlement_reason, settlement_type
from vPositionsSDCutoff pos
join vSettlementsEx sett on sett.asset_id = pos.asset_id
order by pos.account, closing_date


--- FILE: ReportRunner\ReportRunner\SQL\SettlementCashMismatch-MissionControl.sql ---
select s.asset_id
,s.last_name
,s.closing_date
,s.net_settlement_payment [cash_expected_$]
,s.total_cash_received [cash_received_$],
round(s.total_cash_received-s.net_settlement_payment+ISNULL(r.refund, 0),2) [delta_$],
null [___],
s.note_last [note] 
from vSettlementsEx s
left join (select max(date) [date_last], sum(net_amount) [net_amount],s.settlement_id,max(s.descr) [descr_last],max(s.note) [note_last] from vSettlementTransEx s where s.banktranstype_id = 1 group by settlement_id) t on t.settlement_id = s.settlement_id
left join (select net_amount as [refund],s.settlement_id from vSettlementTransEx s where s.banktranstype_id = 3) r on s.settlement_id = r.settlement_id
where (abs(s.total_cash_received-s.net_settlement_payment+ISNULL(r.refund, 0))>1 OR total_cash_received is null) AND s.closing_date between '7/31/2022' and dbo.TodayNY()
order by s.settlement_id desc


--- FILE: ReportRunner\ReportRunner\SQL\SettlementCashMismatch.sql ---
drop table if exists #tmp;

with refunds as
(
select abs(amount) [amount],frbinv_id,transaction_date from vFRBInvEx f where f.account_number like '%3081' and transaction_date>'9/27/2023' and transaction_description ='CHECK'
)
select s.asset_id
,s.last_name
,s.closing_date
,s.net_settlement_payment [cash_expected_$]
,s.total_cash_received [cash_received_$]
,round(s.total_cash_received-s.net_settlement_payment-ISNULL(r.refund, 0),2) [delta_$]
,r.refund [refund_$]
,s.note_last [note]
,null [___]
,re.transaction_date
,re.amount
,null [____]
,s.settlement_id
,re.frbinv_id [banktrans_id]
,3 [banktranstype_id]
into #tmp
from vSettlementsEx s
left join (select max(date) [date_last], sum(net_amount) [net_amount],s.settlement_id,max(s.descr) [descr_last],max(s.note) [note_last] from vSettlementTransEx s where s.banktranstype_id = 1 group by settlement_id) t on t.settlement_id = s.settlement_id
left join (select net_amount as [refund],s.settlement_id from vSettlementTransEx s where s.banktranstype_id = 3) r on s.settlement_id = r.settlement_id
left join refunds re on round(s.total_cash_received-s.net_settlement_payment-ISNULL(r.refund, 0),2) between re.amount - .1 and re.amount + .1
where (abs(s.total_cash_received-s.net_settlement_payment+ISNULL(r.refund, 0))>1 OR total_cash_received is null) AND (s.closing_date between '7/31/2022' and dbo.TodayNY()) AND s.asset_id NOT IN ('24636992803555','72928875564740','79348084297193','304-29-6520','48759859157922')


select asset_id, last_name, closing_date, [cash_expected_$], [cash_received_$], [delta_$], [refund_$], [note] from #tmp where [delta_$] < -0.2 order by closing_date desc

select asset_id, last_name, closing_date, [cash_expected_$], [cash_received_$], [delta_$], [refund_$], [note]  from #tmp where [delta_$] > 1 and [banktrans_id] is null order by closing_date desc

select * from #tmp where [delta_$] > 1 and [banktrans_id] is not null and closing_date < transaction_date order by closing_date desc

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\SettlementCollectionTransfer.sql ---
drop table if exists #tmp;


select distinct
    'TCB' [bank],
    se.asset_id,
    se.last_name,
    se.closing_date,
    se.net_settlement_payment,
    se.settlement_type,
    se.settlement_reason,
    se.cash_to_remit_to_coll_calc [cash_to_coll_calc_|0,000.00|],
    se.net_settlement_payment [net_settlement_payment_|0,000.00|],
    se.account,
    null [___],
    se.settlement_id,
    tt.tcbinv_id [banktrans_id],
    b.banktranstype_id,
    se.account [note]
into #tmp
from dbo.vSettlementTrans st
join dbo.vSettlementsEx se on st.settlement_id = se.settlement_id
left join (
    select s.settlement_id
    from vSettlementTransEx s
    where s.banktranstype_id not in (1,3)
) t on t.settlement_id = st.settlement_id
left join vTCBInvEx tt on se.net_settlement_payment BETWEEN (tt.DebitAmt - 0.10) AND (tt.DebitAmt + 0.10)
left join vBankTransTypes b on b.account_id = se.account_id
where st.banktranstype_id = 1
  and t.settlement_id IS NULL
  and se.closing_date > '7/31/2022'
  and tt.AsOfDate >= se.closing_date 
  and se.net_settlement_payment > 0.05;


insert into #tmp (
    bank,
    asset_id,
    last_name,
    closing_date,
    net_settlement_payment,
    settlement_type,
    settlement_reason,
    [cash_to_coll_calc_|0,000.00|],
    [net_settlement_payment_|0,000.00|],
    account,
    [___],
    settlement_id,
    banktrans_id,
    banktranstype_id,
    note
)
select distinct
    'JPM' [bank],
    se.asset_id,
    se.last_name,
    se.closing_date,
    se.net_settlement_payment,
    se.settlement_type,
    se.settlement_reason,
    se.cash_to_remit_to_coll_calc [cash_to_coll_calc_|0,000.00|],
    se.net_settlement_payment [net_settlement_payment_|0,000.00|],
    se.account,
    null [___],
    se.settlement_id,
    j.jpminv_id [banktrans_id],
    b.banktranstype_id,
    se.account [note]
from dbo.vSettlementTrans st
join dbo.vSettlementsEx se on st.settlement_id = se.settlement_id
left join (
    select s.settlement_id
    from vSettlementTransEx s
    where s.banktranstype_id not in (1,3)
) t on t.settlement_id = st.settlement_id
left join vJPMInvEx j on se.net_settlement_payment BETWEEN (j.amount_dr - 0.10) AND (j.amount_dr + 0.10)
left join vBankTransTypes b on b.account_id = se.account_id
where st.banktranstype_id = 1
  and t.settlement_id IS NULL
  and se.closing_date > '7/31/2022'
  and j.account_number = 80018953081
  and j.asof_date >= se.closing_date;

select bank,
       asset_id,
       last_name,
       closing_date,
       net_settlement_payment,
       settlement_type,
       settlement_reason,
       [cash_to_coll_calc_|0,000.00|],
       account
from #tmp
where banktrans_id is null;

select *
from #tmp
where banktrans_id is not null
order by closing_date, settlement_id;

drop table #tmp;


--- FILE: ReportRunner\ReportRunner\SQL\SettlementHPVariance.sql ---
��d r o p   t a b l e   i f   e x i s t s   # t m p 
 
 
 
 d e c l a r e   @ s i x t y d a y s a g o   d a t e t i m e 
 
 s e t   @ s i x t y d a y s a g o   =   d a t e a d d ( d a y , - 6 0 , d b o . T o d a y N Y ( ) ) 
 
 
 
 s e l e c t   
 
 s r . a s s e t _ i d 
 
 , a . m a x _ i d 
 
 , s r . s t a t e m e n t _ v o i d _ a f t e r 
 
 , a . a c c o u n t 
 
 , s r . s t a t e m e n t _ d a t e 
 
 , s r . s e t t l e m e n t _ t y p e 
 
 , s r . s e t t l e m e n t t y p e _ i d 
 
 , s r . s e t t l e m e n t _ r e a s o n 
 
 , c a s e   w h e n   a . f i n a l _ d i s p o s i t i o n _ d a t e   i s   n o t   n u l l   t h e n   c o n v e r t ( d a t e , f o r m a t ( a . f i n a l _ d i s p o s i t i o n _ d a t e , ' M / 1 / y y y y ' ) )   e l s e   n u l l   e n d   [ s e t t l e m e n t _ m o n t h ] 
 
 , a . u n l o c k _ s h a r e _ e s t i m a t e 
 
 , a . e f f e c t i v e _ d a t e 
 
 , a . f i n a l _ d i s p o s i t i o n _ d a t e 
 
 , c a s e   w h e n   a . f i n a l _ d i s p o s i t i o n _ d a t e   i s   n u l l   t h e n   0   e l s e   1   e n d   [ t e r m i n a t e d ] 
 
 , a . a g e 
 
 , a . s t a r t i n g _ h o m e _ v a l u e 
 
 , a . e n d i n g _ h o m e _ v a l u e 
 
 , a . v a l u a t i o n _ v a l u e _ l a t e s t 
 
 , c a s e   w h e n   a . v a l u a t i o n _ v a l u e _ l a t e s t   i s   n u l l   t h e n   n u l l   e l s e   r o u n d ( a . v a l u a t i o n _ c o n f i d e n c e _ l a t e s t , 0 )   e n d   [ C O N F I D E N C E ] 
 
 , a . h o m e _ v a l u e _ h p i _ l a t e s t 
 
 , a . c r e d i t _ s c o r e 
 
 , a . c r e d i t _ s c o r e _ c a l c _ c u r r e n t 
 
 , a . e x c h a n g e _ r a t e 
 
 , a . c o s t _ l i m i t 
 
 , a . l t v 
 
 , f o r m a t ( ( ( a . s e c u r e d _ d e b t + a . i n v e s t m e n t _ p a y m e n t _ c u r r e n t ) * 1 . 0 ) / ( a . s t a r t i n g _ h o m e _ v a l u e * 1 . 0 ) , ' P ' )   [ C L T V ] 
 
 , a . t o t a l _ h o m e _ f i n a n c e 
 
 , a . t o t a l _ h o m e _ f i n a n c e _ l i m i t 
 
 , a . s t a t e 
 
 , L E F T ( a . m s a _ n a m e , L E N ( a . m s a _ n a m e ) - 4 )   [ M S A _ N A M E ] 
 
 , c a s e   w h e n   a . v a l u a t i o n _ v a l u e _ l a t e s t   i s   n u l l   t h e n   ( a . e n d i n g _ h o m e _ v a l u e - a . s t a r t i n g _ h o m e _ v a l u e ) / a . s t a r t i n g _ h o m e _ v a l u e   e l s e   ( a . e n d i n g _ h o m e _ v a l u e - a . v a l u a t i o n _ v a l u e _ l a t e s t ) / a . v a l u a t i o n _ v a l u e _ l a t e s t   e n d   [ D E L T A _ % ] 
 
 , c a s e   w h e n   a . h o m e _ v a l u e _ h p i _ l a t e s t   i s   n o t   n u l l   t h e n   ( a . e n d i n g _ h o m e _ v a l u e - a . h o m e _ v a l u e _ h p i _ l a t e s t ) / a . h o m e _ v a l u e _ h p i _ l a t e s t   e n d   [ H P I _ A D J _ D E L T A _ % ] 
 
 i n t o   # t m p   f r o m   v S e t t l e m e n t R e q u e s t s E x   s r 
 
 j o i n   v A s s e t s P o s i t i o n E x   a   o n   s r . a s s e t _ i d   =   a . a s s e t _ i d 
 
 w h e r e   s r . l a t e s t = 1 
 
 - - S E T T L E M E N T   H P   V A R I A N C E   B Y   M O N T H 
 
 s e l e c t   s e t t l e m e n t _ m o n t h   [ m o n t h ] ,   s u m ( m o n t h l y _ s e t t l e m e n t s )   [ # _ S E T T L E M E N T S ] ,   s u m ( m o n t h l y _ b u y o u t s )   [ # _ B U Y O U T S ] ,   s u m ( m o n t h l y _ h o m e _ s a l e s )   [ # _ H O M E _ S A L E S ] ,   f o r m a t ( ( s u m ( [ D E L T A _ % ] ) ) / ( s u m ( m o n t h l y _ s e t t l e m e n t s ) ) , ' P ' )   [ M O N T H L Y _ D E L T A _ % ] ,   f o r m a t ( ( s u m ( [ H P I _ A D J _ D E L T A _ % ] ) ) / ( s u m ( m o n t h l y _ s e t t l e m e n t s ) ) , ' P ' )   [ H P I _ A D J _ �_ % ] 
 
 , f o r m a t ( ( s u m ( [ B U Y O U T _ D E L T A _ % ] ) ) / ( n u l l i f ( s u m ( [ M O N T H L Y _ B U Y O U T S ] ) , 0 ) ) , ' P ' )   [ B U Y O U T _ �_ % ] , f o r m a t ( ( s u m ( [ H O M E _ S A L E _ D E L T A _ % ] ) ) / ( n u l l i f ( s u m ( [ M O N T H L Y _ H O M E _ S A L E S ] ) , 0 ) ) , ' P ' )   [ H O M E _ S A L E _ �_ % ]   f r o m 
 
 ( s e l e c t   s e t t l e m e n t _ m o n t h 
 
 , c o u n t ( * )   [ M O N T H L Y _ S E T T L E M E N T S ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 1   t h e n   1   e l s e   0   e n d )   [ M O N T H L Y _ B U Y O U T S ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 2   t h e n   1   e l s e   0   e n d )   [ M O N T H L Y _ H O M E _ S A L E S ] 
 
 , s u m ( [ D E L T A _ % ] )   [ D E L T A _ % ] 
 
 , s u m ( [ H P I _ A D J _ D E L T A _ % ] )   [ H P I _ A D J _ D E L T A _ % ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 1   t h e n   [ D E L T A _ % ]   e l s e   0   e n d )   [ B U Y O U T _ D E L T A _ % ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 2   t h e n   [ D E L T A _ % ]   e l s e   0   e n d )   [ H O M E _ S A L E _ D E L T A _ % ] 
 
 f r o m   # t m p 
 
 w h e r e   t e r m i n a t e d = 1   a n d   s e t t l e m e n t _ m o n t h > ' 1 1 / 1 / 2 0 2 2 ' 
 
 g r o u p   b y   s e t t l e m e n t _ m o n t h 
 
 )   t   g r o u p   b y   s e t t l e m e n t _ m o n t h   o r d e r   b y   s e t t l e m e n t _ m o n t h   d e s c 
 
 - - S E T T L E M E N T   H P   V A R I A N C E   B Y   M O N T H   &   S T A T E 
 
 ; w i t h   c t e   a s ( 
 
 s e l e c t   s e t t l e m e n t _ m o n t h ,   s t a t e ,   s u m ( m o n t h l y _ s e t t l e m e n t s )   [ # _ S E T T L E M E N T S ] ,   s u m ( m o n t h l y _ b u y o u t s )   [ # _ B U Y O U T S ] ,   s u m ( m o n t h l y _ h o m e _ s a l e s )   [ # _ H O M E _ S A L E S ] ,   f o r m a t ( ( s u m ( [ D E L T A _ % ] ) ) / ( s u m ( m o n t h l y _ s e t t l e m e n t s ) ) , ' P ' )   [ M O N T H L Y _ D E L T A _ % ] ,   f o r m a t ( ( s u m ( [ H P I _ A D J _ D E L T A _ % ] ) ) / ( s u m ( m o n t h l y _ s e t t l e m e n t s ) ) , ' P ' )   [ H P I _ A D J _ �_ % ]   
 
 , f o r m a t ( ( s u m ( [ B U Y O U T _ D E L T A _ % ] ) ) / ( n u l l i f ( s u m ( [ M O N T H L Y _ B U Y O U T S ] ) , 0 ) ) , ' P ' )   [ B U Y O U T _ �_ % ] , f o r m a t ( ( s u m ( [ H O M E _ S A L E _ D E L T A _ % ] ) ) / ( n u l l i f ( s u m ( [ M O N T H L Y _ H O M E _ S A L E S ] ) , 0 ) ) , ' P ' )   [ H O M E _ S A L E _ �_ % ] 
 
 , [ r 1 ]   =   R O W _ N U M B E R ( )   O V E R ( P A R T I T I O N   B Y   [ s e t t l e m e n t _ m o n t h ]   O R D E R   B Y   [ s e t t l e m e n t _ m o n t h ] ) 
 
 f r o m   ( s e l e c t   s e t t l e m e n t _ m o n t h 
 
 , s t a t e 
 
 , c o u n t ( * )   [ M O N T H L Y _ S E T T L E M E N T S ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 1   t h e n   1   e l s e   0   e n d )   [ M O N T H L Y _ B U Y O U T S ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 2   t h e n   1   e l s e   0   e n d )   [ M O N T H L Y _ H O M E _ S A L E S ] 
 
 , s u m ( [ D E L T A _ % ] )   [ D E L T A _ % ] 
 
 , s u m ( [ H P I _ A D J _ D E L T A _ % ] )   [ H P I _ A D J _ D E L T A _ % ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 1   t h e n   [ D E L T A _ % ]   e l s e   0   e n d )   [ B U Y O U T _ D E L T A _ % ] 
 
 , s u m ( c a s e   w h e n   s e t t l e m e n t t y p e _ i d = 2   t h e n   [ D E L T A _ % ]   e l s e   0   e n d )   [ H O M E _ S A L E _ D E L T A _ % ] 
 
 f r o m   # t m p 
 
 w h e r e   t e r m i n a t e d = 1   a n d   s e t t l e m e n t _ m o n t h > ' 1 1 / 1 / 2 0 2 2 ' 
 
 g r o u p   b y   s e t t l e m e n t _ m o n t h , s t a t e 
 
 )   t   g r o u p   b y   s e t t l e m e n t _ m o n t h , s t a t e ) 
 
 s e l e c t   c a s e   w h e n   [ r 1 ]   =   1   t h e n   [ s e t t l e m e n t _ m o n t h ]   e l s e   n u l l   e n d   [ m o n t h ] ,   s t a t e ,   [ # _ S E T T L E M E N T S ] ,   [ # _ B U Y O U T S ] ,   [ # _ H O M E _ S A L E S ] ,   [ M O N T H L Y _ D E L T A _ % ] ,   [ H P I _ A D J _ �_ % ] ,   [ B U Y O U T _ �_ % ] ,   [ H O M E _ S A L E _ �_ % ]   f r o m   c t e   o r d e r   b y   c t e . [ s e t t l e m e n t _ m o n t h ]   d e s c , [ r 1 ] 
 
   - - T O P   &   W O R S T   1 0   P E R F O R M E R S - - 
 
 s e l e c t   t o p   1 0   a s s e t _ i d ,   [ D E L T A _ % ] ,   s t a t e ,   m s a _ n a m e     f r o m   # t m p   w h e r e   t e r m i n a t e d = 1   a n d   f i n a l _ d i s p o s i t i o n _ d a t e > = @ s i x t y d a y s a g o   o r d e r   b y   [ D E L T A _ % ]   d e s c 
 
 s e l e c t   t o p   1 0   a s s e t _ i d ,   [ D E L T A _ % ] ,   s t a t e ,   m s a _ n a m e     f r o m   # t m p   w h e r e   t e r m i n a t e d = 1   a n d   f i n a l _ d i s p o s i t i o n _ d a t e > = @ s i x t y d a y s a g o   o r d e r   b y   [ D E L T A _ % ]   a s c 
 
 - - F I N A L   S E T T L E M E N T   D E T A I L S   L A S T   6 0   D A Y S 
 
 s e l e c t   a s s e t _ i d 
 
 , m a x _ i d 
 
 , a c c o u n t 
 
 , e f f e c t i v e _ d a t e 
 
 , f i n a l _ d i s p o s i t i o n _ d a t e   [ C L O S I N G _ D A T E ] 
 
 , s e t t l e m e n t _ t y p e 
 
 , s e t t l e m e n t _ r e a s o n 
 
 , u n l o c k _ s h a r e _ e s t i m a t e   [ U N L O C K _ S H A R E _ | 0 , 0 0 0 | ] 
 
 , a g e 
 
 , c a s e   w h e n   a g e   <   7   t h e n   ' T R U E '   e l s e   ' F A L S E '   e n d   [ L E S S _ T H A N _ 6 _ M O S ] 
 
 , [ D E L T A _ % ] 
 
 , s t a r t i n g _ h o m e _ v a l u e 
 
 , c a s e   w h e n   v a l u a t i o n _ v a l u e _ l a t e s t   i s   n u l l   t h e n   n u l l   e l s e   v a l u a t i o n _ v a l u e _ l a t e s t   e n d   [ L A T E S T _ V A L U A T I O N _ | 0 , 0 0 0 | ] 
 
 , c a s e   w h e n   v a l u a t i o n _ v a l u e _ l a t e s t   i s   n u l l   t h e n   n u l l   e l s e   r o u n d ( C O N F I D E N C E , 0 )   e n d   [ C O N F I D E N C E _ | 0 | ] 
 
 , h o m e _ v a l u e _ h p i _ l a t e s t   [ L A T E S T _ H P I _ A D J _ V A L U A T I O N _ | 0 , 0 0 0 | ] 
 
 , [ H P I _ A D J _ D E L T A _ % ] 
 
 , e n d i n g _ h o m e _ v a l u e 
 
 , c r e d i t _ s c o r e   [ O R I G _ C R E D I T _ S C O R E _ | 0 | ] 
 
 , c r e d i t _ s c o r e _ c a l c _ c u r r e n t   [ C U R R _ C R E D I T _ S C O R E ] 
 
 , e x c h a n g e _ r a t e 
 
 , c o s t _ l i m i t   [ A C L _ % ] 
 
 , L T V 
 
 , C L T V 
 
 , t o t a l _ h o m e _ f i n a n c e   [ T H F _ % ] 
 
 , t o t a l _ h o m e _ f i n a n c e _ l i m i t   [ T H F L _ % ] 
 
 , s t a t e 
 
 , m s a _ n a m e 
 
 f r o m   # t m p   w h e r e   f i n a l _ d i s p o s i t i o n _ d a t e > = @ s i x t y d a y s a g o   o r d e r   b y   [ D E L T A _ % ]   a s c 
 
 - - A C T I V E   S E T T L E M E N T   R E Q U E S T   D E T A I L S 
 
 s e l e c t   a s s e t _ i d 
 
 , a c c o u n t 
 
 , e f f e c t i v e _ d a t e 
 
 , s t a t e m e n t _ v o i d _ a f t e r 
 
 , s e t t l e m e n t _ t y p e 
 
 , s e t t l e m e n t _ r e a s o n 
 
 , u n l o c k _ s h a r e _ e s t i m a t e   [ U N L O C K _ S H A R E _ | 0 , 0 0 0 | ] 
 
 , a g e 
 
 , c a s e   w h e n   a g e   <   7   t h e n   ' T R U E '   e l s e   ' F A L S E '   e n d   [ L E S S _ T H A N _ 6 _ M O S ] 
 
 , [ D E L T A _ % ] 
 
 , s t a r t i n g _ h o m e _ v a l u e 
 
 , c a s e   w h e n   v a l u a t i o n _ v a l u e _ l a t e s t   i s   n u l l   t h e n   n u l l   e l s e   v a l u a t i o n _ v a l u e _ l a t e s t   e n d   [ L A T E S T _ V A L U A T I O N _ | 0 , 0 0 0 | ] 
 
 , c a s e   w h e n   v a l u a t i o n _ v a l u e _ l a t e s t   i s   n u l l   t h e n   n u l l   e l s e   C O N F I D E N C E   e n d   [ C O N F I D E N C E _ | 0 | ] 
 
 , h o m e _ v a l u e _ h p i _ l a t e s t   [ L A T E S T _ H P I _ A D J _ V A L U A T I O N _ | 0 , 0 0 0 | ] 
 
 , [ H P I _ A D J _ D E L T A _ % ] 
 
 , e n d i n g _ h o m e _ v a l u e 
 
 , c r e d i t _ s c o r e   [ O R I G _ C R E D I T _ S C O R E _ | 0 | ] 
 
 , c r e d i t _ s c o r e _ c a l c _ c u r r e n t   [ C U R R _ C R E D I T _ S C O R E ] 
 
 , e x c h a n g e _ r a t e 
 
 , c o s t _ l i m i t   [ A C L _ % ] 
 
 , L T V 
 
 , C L T V 
 
 , t o t a l _ h o m e _ f i n a n c e   [ T H F _ % ] 
 
 , t o t a l _ h o m e _ f i n a n c e _ l i m i t   [ T H F L _ % ] 
 
 , s t a t e 
 
 , m s a _ n a m e 
 
 f r o m   # t m p   w h e r e   t e r m i n a t e d = 0   a n d   s t a t e m e n t _ v o i d _ a f t e r > = d b o . T o d a y N Y ( )   o r d e r   b y   [ D E L T A _ % ]   a s c 
 
 
 
 d r o p   t a b l e   # t m p 


--- FILE: ReportRunner\ReportRunner\SQL\ShipmentsWithMultipleDC.sql ---
select collatshipment_id,doc_custodian_name from vCollatShipmentsEx where doc_custodian_name is not null and shipped=0 group by collatshipment_id,doc_custodian_name order by collatshipment_id,doc_custodian_name

select collatshipment_id,doc_custodian_name,asset_id,name_simple + ' - ' + address_simple [name_-_address],max(nice_name) nice_name,max(tracking_number) [tracking_number] from vCollatShipmentsEx where doc_custodian_name is not null and shipped=0 and (collatshipment_id in (select collatshipment_id FROM vCollatShipmentsEx where (asset_id is not null and doc_custodian_name is not null) group by collatshipment_id having count(distinct(checksum(collatshipment_id,doc_custodian_name)))>1)) group by asset_id, collatshipment_id,doc_custodian_name,name_simple,address_simple order by collatshipment_id,doc_custodian_name

select collatshipment_id,doc_custodian_name,asset_id,name_simple + ' - ' + address_simple [name_-_address],max(nice_name) nice_name,max(tracking_number) [tracking_number] from vCollatShipmentsEx where doc_custodian_name is not null and shipped=1 and (collatshipment_id in (select collatshipment_id FROM vCollatShipmentsEx where (asset_id is not null and doc_custodian_name is not null) group by collatshipment_id having count(distinct(checksum(collatshipment_id,doc_custodian_name)))>1)) group by asset_id, collatshipment_id,doc_custodian_name,name_simple,address_simple order by collatshipment_id,doc_custodian_name

select collatshipment_id,nice_name,tracking_number from vCollatShipmentsEx where asset_id is null 

select distinct collatshipment_id, nice_name from vCollatShipmentsEx order by collatshipment_id


--- FILE: ReportRunner\ReportRunner\SQL\snowflake_sync_status.sql ---
drop table if exists #tmp
drop table if exists #rows

select max(LastUpdate) [LastUpdate],destname,convert(int,null) [SourceRowCount],convert(int,null) [DestRowCount] into #tmp from Status_SnowFlake_Sync where destname not like '_%test' and DestName is not null group by destname

update t set SourceRowCount = s.SourceRowCount from #tmp t join Status_SnowFlake_Sync s on s.LastUpdate = t.LastUpdate and t.DestName = s.DestName

SELECT TBL.object_id, TBL.name, SUM(PART.rows) AS rows into #rows
FROM sys.tables TBL
INNER JOIN sys.partitions PART ON TBL.object_id = PART.object_id
INNER JOIN sys.indexes IDX ON PART.object_id = IDX.object_id
AND PART.index_id = IDX.index_id
WHERE 
IDX.index_id < 2
GROUP BY TBL.object_id, TBL.name;

update t set DestRowCount = r.rows from #tmp t join #rows r on r.name = t.DestName

select * from #tmp where cast(LastUpdate as Date) != cast(GetDate() as Date) or DestRowCount != SourceRowCount

drop table if exists #tmp
drop table if exists #rows


--- FILE: ReportRunner\ReportRunner\SQL\solar_lien_position.sql ---
select 
	app.external_id as 'asset_id' 
	,address_simple
	, trade.lien_position as 'solar_lien_position'
	, asset.lien_position as 'unlock_lien_position'
	, case when trade.lien_position <= asset.lien_position then 'Solar Lien Position Needs Review ' else 'looks good' end as 'Solar_Lien_Status'
from api_tradeline trade
left join api_application app on app.id = trade.application_id
join vassets asset on  asset.asset_id = convert(varchar(255),app.external_id)
where is_subject_property = 1
and account_type = 'solar'
order by Solar_Lien_Status


--- FILE: ReportRunner\ReportRunner\SQL\Stored Proc UAM.dbo.ConsolidatedMissingData.sql ---
SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
ALTER proc [dbo].[ConsolidatedMissingData] @asset_id varchar(30) = null, @display_summary bit = 0, @detail_badger bit = 0, @include_closed bit = 1
as
begin


  
  drop table if exists #missing
  drop table if exists #d
  drop table if exists #a
  drop table if exists #ae
  drop table if exists #v
  drop table if exists #p

 declare @threshold float = 0.0
 declare @is_max bit = 0

 select * into #a from vAssetsEx a where 1=2
 select * into #ae from vApplicantsEx where 1=2
 
 insert into #a select * from vAssetsEx a where ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id)
 if((select count(*) from #a) = 0 )
 begin
  alter table #a alter column address_full varchar(max) null
  insert into #a select * from vAssetsMaxEx a where ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id) 
  insert into #ae select * from vApplicantsMaxEx ae where (@asset_id is null or ae.asset_id = @asset_id)
  select @is_max = 1
 end
 else
 begin
  insert into #ae select * from vApplicantsEx ae where (@asset_id is null or ae.asset_id = @asset_id)
 end

 
 
 select * into #v from vValuations ae where (@asset_id is null or ae.asset_id = @asset_id)
 select * into #p from vPayoffs ae where (@asset_id is null or ae.asset_id = @asset_id)
 
 select d.asset_id,balance,rate,payment,d.lien_position,credit_limit,princ_payoff_amt,d.account_closed,account_open_date,a.secured_debt, sum(d.balance_calc) [balance_calc],d.debttype_id,l.name [lender_name] into #d from vDebt d join #a a on a.asset_id = d.asset_id left join Lenders l on l.id = d.lender_id where ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id) group by d.asset_id,balance,rate,payment,d.lien_position,credit_limit,princ_payoff_amt,balance_calc,a.secured_debt,d.account_closed,account_open_date,d.debttype_id,l.[name]
 

  create table #missing
  (
    asset_id varchar(30)
    , integritycheck_id int
    , single_person varchar(100)
    
    , [value] varchar(250)
    , priority_id int 
    , row_color varchar(30)
    , foreignid_id int
    , foreignidtype_id int
  )

  INSERT INTO #missing (asset_id,integritycheck_id,value) 
  select asset_id,2,credit_score from #a a where a.credit_score is null 

  INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 3 
     , cs.credit_score
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
        left join vCreditScores cs on ae.applicant_id = cs.applicant_id and cs.initial = 1
    where
        cs.credit_score is null    


  INSERT INTO #missing (asset_id,integritycheck_id,value)
  select
  a.asset_id
  , 97 
  , 'CR: ' + format(sum(ctl.balance/1000.0),'0') + 'k BADGER: ' + format(sum(a.secured_debt/1000.0),'0') + 'k P/O: ' + FORMAT(sum(isnull(d.princ_payoff_amt,0)),'0') + 'k'
  
  from
    vAssetApplicantSingle aas 
    join vCreditFiles crs on crs.applicant_id = aas.applicant_id and isnull(crs.applicant_co_id,'') = isnull(aas.applicant_co_id,'')
    join vCRTradelines ctl on ctl.creditfile_id = crs.creditfile_id and open_close = 'Open' and acct_type = 'Mortgage'
    join #a a on a.asset_id = aas.asset_id and (a.asset_id = @asset_id or @asset_id is null)
    left join #d d on d.asset_id = a.asset_id
    
 where
  crs.initial_api = 1
  
 group by 
  a.asset_id
  , crs.creditfile_id
  , a.name_simple
  , a.address_simple
  having
    sum(a.secured_debt)< sum(ctl.balance*.97)
  order by
    sum(a.secured_debt)-sum(ctl.balance)
    
    
    
  INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 51 
     , ae.last_name
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        (AE.last_name like '% Sr.' OR AE.last_name like '% Jr.' OR AE.last_name like '% III')
        
        
      INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 65 
     , ae.email
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        dbo.CheckValidEmail(ae.email) != 1
        
        
    INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 52 
     , FORMAT(ae.dob,'MM/dd/yyyy')
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        DATEPART(yy, ae.dob) <= 1900
        
    INSERT INTO #missing (asset_id,integritycheck_id,value)
    select 
      a.asset_id
     , 77 
     , convert(varchar(30),ae.dob)
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        age_at_origination_youngest <= 21
        
        INSERT INTO #missing (asset_id,integritycheck_id,value)
    select 
      a.asset_id
     , 96 
     , a.zip
      from 
        #a a
   
    where
        len(zip) != 5
        
        
        
    INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 53 
     , convert(varchar(30),ae.full_name)
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        a.first_name like '% %' or a.last_name like '% %' or a.first_name like '%.%' or a.last_name like '%.%'


  iNSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 55 
     , convert(varchar(30),ae.full_name)
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        a.first_name like '%.%'
        
  INSERT INTO #missing (asset_id,integritycheck_id) 
  select 
    a.asset_id
    , 4 
      from 
        #a a
      where
       a.closingagent_id is null
      order by
        effective_date asc

INSERT INTO #missing (asset_id,integritycheck_id) 
  select 
    a.asset_id
    , 92 
      from 
        #a a
      where
       a.credit_score < 550 and a.exchange_rate < 1.7
      order by
        effective_date asc
        
  INSERT INTO #missing (asset_id,integritycheck_id) 
  select 
    a.asset_id
    , 87 
      from 
        #a a
      where
       a.title_held_in_type_id is null
      order by
        effective_date asc
        
  INSERT INTO #missing (asset_id,integritycheck_id,single_person)
  select 
    ap.asset_id
    ,5 
    , ap.full_name
    
      from 
        #ae ap
        left join #a a on ap.asset_id = a.asset_id
      where
      ap.ssn_last4 is null
      and ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id)
    
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 6 
      from 
        #a a
    where
      a.doc_consent_of_spouse is null
    
  INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,7 
      from 
        #a a
    where
      a.origination_fee is null
      

  INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     
    select 
      a.asset_id
      ,54 
      ,a.cost_limit
      from 
        #a a
    where
      (a.cost_limit != .18 and a.cost_limit_basis!=A.INVESTMENT_PAYMENT)
      OR
      (a.cost_limit = .18 and a.cost_limit_basis!=a.investment_payment-a.origination_fee)
      
      
   INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     
    select 
      a.asset_id
      ,95 
      ,a.cost_limit
      from 
        #a a
    where 
    a.cost_limit_basis = a.investment_payment
   and a.lockout_months is not null
      
  INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     

  select
   a.asset_id
   , 66 
   , 'MTG: ' + format(d.balance,'0,###') + ' P/O: ' + format(p.payoff_final,'0,###')
    from 
      #a a 
      join #d d on d.asset_id = a.asset_id
      join #p p on d.asset_id = P.asset_id AND d.balance = p.payoff_final
    WHERE
    balance_calc != 0
      

  INSERT INTO #missing (asset_id,integritycheck_id,[value])  
    select
    p.asset_id
    , 67 
    , 'P/O: ' + p.account_name + ' - ' + format(p.payoff_final,'0,###') + 'k' + CASE WHEN d.lender_name is not null then ' vs Debt: ' + format(d.balance,'0,###') + 'k' else '' end
      from 
        #a a 
        join #p p on a.asset_id = P.asset_id
        left join #d d on d.asset_id = p.asset_id  and p.account_name = d.lender_name
      where
        (P.mortgage_debt = 0 OR P.MORTGAGE_DEBT IS NULL)
        and
        (

          (
          d.lender_name IS NOT NULL
          or
          (account_name like '%Funding%' or account_name like '%Mortgage%' or account_name like '%Loan%' or account_name like '%Funding%' or account_name like '%Bank%' or account_name like '%Credit Union%' or account_name like '% CU%'))
          
          or
          d.asset_id is not null
        )
      
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 20 
      from 
        #a a
    where
      a.max_proceeds is null
      

 
  INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     
    select 
      a.asset_id
      ,8 
      , CONVERT(VARCHAR(30),format(a.investment_payment-a.max_proceeds ,'0,000'))
      from 
        #a a
    where
      a.investment_payment-a.max_proceeds > 1.0
      
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,9 
      from 
        #a a
    where
      a.proceedsuse_id is null

   
    INSERT INTO #missing (asset_id,integritycheck_id,[value])     
    select 
      D.asset_id
      ,39 
      , format(balance_calc-secured_debt,'0,###')
      from 
        (select sum(balance_calc) [balance_calc],asset_id,min(secured_debt) [secured_debt] from #d s where s.account_closed is null group by asset_id) d 
        where
          ABS(CONVERT(int, balance_calc-secured_debt))>@threshold 
     
      
  
    
    INSERT INTO #missing (asset_id,integritycheck_id,value)     
    select 
      d.asset_id
      ,40 
      , format(balance-princ_payoff_amt,'0,###')
      from 
        #d d
    where
      (balance-princ_payoff_amt) < -@threshold 
    
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,10 
      from 
        #d a
    where
      a.rate >= .25 and a.account_closed is null
      
            
  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 36 
    from 
      #a a 
      left join #d c on a.asset_id = c.asset_id
    where
      c.rate is null and a.lien_position != 1 and (c.balance_calc > 1 or c.account_closed is null)
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 11 
      from 
        #a a
    where
      a.purchase_amount IS NULL
    
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 12 
      from 
        #a a
    where
      a.purchase_date IS NULL
      
          INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 13 
      from 
        #a a
    where
      a.term != 120
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 14 
      from 
        #d a
    where
      a.account_open_date is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 15 
      from 
        #a a
    where
      a.doc_maintenance_addendum is null

      
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 16 
      from 
        #a a
    where
      a.credit_score < 550 and a.dti is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 86 
      from 
        #a a
    where
      a.credit_score = 0 
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 17 
      from 
        #a a
    where
      a.dscr is null and a.is_rental = 1
   
    INSERT INTO #missing (asset_id,integritycheck_id,[value])     
    select 
      a.asset_id
      , 74 
      , a.apn
      from 
        #a a
    where
      a.apn in ('Principal Residence')

    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 18 
      from 
        #a a
    where
      a.dti > 1.0
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 19 
      from 
        #a a
    where
      a.legal_desc is null
      
      
        INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 21 
      from 
        #a a
    where
      a.legal_desc is not null and (charindex(a.county,a.legal_desc)=0 or charindex(a.county,a.legal_desc) is null)
    
            INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 49 
      from 
        #a a
    where
      (charindex('COUNTY',a.county)<>0)
      
     
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 22 
      from 
        #a a
    where
      a.folder_name_ups is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 23 
      from 
        #a a
    where
      a.propertycondition_id is null

    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 24 
      from 
        #a a
    where
      a.secured_debt is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 25 
      from 
        #a a
    where
      a.secured_debt = 0 and a.lien_position != 1
      
      
      INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 26 
      from 
        #a a
    where
      a.secured_debt >= starting_home_value
      
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 76 
      from 
        #a a
    where
      a.credit_score <= 550 and a.is_rental = 1
      
      
      
         INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 27 
      from 
        #a a
    where
      a.total_home_finance > a.total_home_finance_limit
     

        INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 28 
      from 
        #a a
    where
      a.propertytype_id is null

        INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 46 
      from 
        #a a
    where
      a.county in ('USA')
      
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 29 
      from 
        #a a
    where
      a.beds is null or a.baths is null or a.sqft is null
      

  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    d.asset_id
    
    
    , 30 
    
    from 
      #d d
        join #a a on a.asset_id = d.asset_id
    where
      
      (d.balance_calc != 0)
    group by
      d.asset_id
      , a.lien_position
    having
      count(*)+1 != a.lien_position
  
      

  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 31 
    from 
      #a a 
      left join #d c on a.asset_id = c.asset_id
    where
      c.asset_id is null and a.secured_debt != 0
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 38 
    from 
      #a a 
      left join #d d on a.asset_id = d.asset_id
    where
      
      d.debttype_id is null and a.secured_debt != 0 and d.account_closed is null
      

      
    INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 37 
    from 
      #a a 
      left join #d D on a.asset_id = D.asset_id
    where
      d.payment is null and a.secured_debt != 0 and d.account_closed is null
    
      
  INSERT INTO #missing (asset_id,integritycheck_id,[value])     
  select 
    a.asset_id
    
    
    , 57 
    , CONVERT(VARCHAR(30),format(a.starting_home_value/1000.0,'###k') + ' vs ' + format(v.value/1000.0,'###k') + ' (' + format((a.starting_home_value-v.value)/1000.0,'###k') + ' diff)') 
    from 
      #a a 
      join #v v on a.asset_id = v.asset_id
    where
      a.starting_home_value > v.[value]
      and v.valuationtype_id IN (21,22)
      
      
   INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id

    , 78 
    from 
      #a a 
      left join #v v on a.asset_id = v.asset_id and v.initial_uw = 1
    
      GROUP BY a.asset_id
      HAVING count(*) = 0 
      
      
      
      
      
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 32 
    from 
      #a a 
      left join vInsurance c on a.asset_id = c.asset_id
    where
      c.asset_id is null
      
      
  INSERT INTO #missing (asset_id,integritycheck_id,[value])     
  select 
    a.asset_id
    
    
    , 41 
    , convert(varchar(30),cs.credit_score) + ' Deal vs ' + convert(varchar(30),cs.credit_score_calc) + ' Calc'
    from 
      #a a 
      left join vCreditScoreAsset cs on a.asset_id = cs.asset_id AND INITIAL = 1
    where
      cs.credit_score != credit_score_calc
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
      SELECT 
     ae.asset_id
     , 33 
    
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  where
    ae.maritalstatus_id = 2
    
  GROUP by
    ae.asset_id
    , a.asset_id
    , ae.maritalstatus_id
    , a.doc_consent_of_spouse
  having
    count(*) = 1
    and doc_consent_of_spouse = 0
    
    
   INSERT INTO #missing (asset_id,integritycheck_id,[value])     
      SELECT 
     ae.asset_id
     , 71 
     , mailing_address_full
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  where
    mailing_address_full is not null and (mailing_address_1 is null or mailing_state is null or mailing_zip is null)
    
    
    
       INSERT INTO #missing (asset_id,integritycheck_id,[value])     
      SELECT 
     ae.asset_id
     , 73 
     , mailing_address_full + ' & ' + address_full
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  where
    mailing_address_1 IS not null and (mailing_address_1 = address_1)
    
    
    
    
  INSERT INTO #missing (asset_id,integritycheck_id)     
        SELECT 
     ae.asset_id
     , 50 
    
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  
    
    
    
  GROUP by
    ae.asset_id
  having
    count(distinct(ae.ssn_last4)) != count(*)

   INSERT INTO #missing (asset_id,integritycheck_id,[value])     
    select 
      a.asset_id
     , 98 
	  , convert(varchar(30),uw.credit_score) + ' FICO & ' + format(a.total_home_finance_limit,'0.0%') + ' THFL'
      from 
        #a a
		join vUnderwriting uw on a.asset_id = uw.asset_id
    where
      a.total_home_finance_limit > .8  AND
	  (uw.credit_score > 499  AND uw.credit_score < 620)
   
   INSERT INTO #missing (asset_id,integritycheck_id,[value])  
   select 
      a.asset_id
     , 99 
	  , convert(varchar(30),uw.credit_score) + ' FICO & ' + format(a.total_home_finance_limit,'0.0%') + ' THFL'
      from 
        #a a
		join vUnderwriting uw on a.asset_id = uw.asset_id
    where
      a.total_home_finance_limit > .85  AND
	  (uw.credit_score > 619 AND uw.credit_score < 700)
     
     INSERT INTO #missing (asset_id,integritycheck_id,[value])  
      select 
      a.asset_id
     , 100 
	  , convert(varchar(30),uw.credit_score) + ' FICO & ' + format(a.total_home_finance_limit,'0.0%') + ' THFL'
      from 
        #a a
		join vUnderwriting uw on a.asset_id = uw.asset_id
    where
     a.total_home_finance_limit > .9  AND
	  uw.credit_score > 699
     
	INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,94 
      from 
        #a a
    where
      CAST(a.origination_fee_pct as decimal(2, 2)) != 0.03
      
         
    

INSERT INTO #missing (asset_id,integritycheck_id)
SELECT 
  a.asset_id
  
  
  , 35
  FROM 
  #A a 
  join vStateReqs s on (s.state = a.state)
  join Fields f on s.db_field = field
  where 
    s.statereqtype_id = 1
    and case when s.db_field = 'legal_desc_short' then a.legal_desc_short else null end is null

update m set priority_id= p.id from #missing m join IntegrityChecks ic on ic.id = m.integritycheck_id join Priorities p on p.id = ic.priority_id

update m set foreignid_id = f.foreignid_id from #missing m left join vForeignIds f on f.asset_id = m.asset_id and f.foreignidtype_id = 2 and m.integritycheck_id = f.foreign_id

if(@is_max=1)
  delete from #missing where integritycheck_id in (select id from IntegrityChecks where max_eligible = 0)



if @display_summary = 1
begin
  select
    count(*) [#]
    , i.check_name [exception]
  from
    #missing m
    join vIntegrityChecks i on i.integritycheck_id = m.integritycheck_id
    left join vNotesEx n on m.foreignid_id = n.foreignid_id and n.latest_foreign = 1
  where
      @include_closed = 1 or (n.is_open is null or n.is_open = 1)
      and i.active = 1
  group by i.check_name
  order by count(*) desc
end

if(@detail_badger = 1)
begin
  select
    a.asset_id
    
    , coalesce(m.single_person,a.name_simple) [name]
    
    , a.address_simple
    , c.check_name [exception]
    , m.value [value]
    , c.check_name
    
    , p.name_alt [priorityname_alt]
    , p.row_color
    , 'priorityname_alt' [col_color]
    , P.RANK
    , c.integritycheck_id
    , n.note
    
    
    
    
    , n.is_open
    , m.foreignid_id
    
    , m.foreignidtype_id
    , p.id [priority_id]
    , n.note_base_id
  from
    #missing m
    left join #a a on a.asset_id = m.asset_id
    left join vIntegrityChecks c on c.integritycheck_id = m.integritycheck_id
    left join Priorities p on p.id = m.priority_id
    
    left join vNotesEx n on m.foreignid_id = n.foreignid_id and n.latest_foreign = 1
    
    where
      @include_closed = 1 or (n.is_open is null or n.is_open = 1)
      and c.active = 1
  order by
    a.effective_date desc
    , P.RANK
    , coalesce(m.single_person,a.name_simple)
    , c.check_name
end
else
begin
  select
    p.name_alt [priority]
    , a.asset_id
    
    , coalesce(m.single_person,a.name_simple) [name]
    
    
    , c.check_name [exception]
    , m.value [value]
    
    
    
    
    
    
        , c.integritycheck_id
    , n.note
    
    
    
    
    , n.is_open
    
  from
    #missing m
    left join #a a on a.asset_id = m.asset_id
    left join vIntegrityChecks c on c.integritycheck_id = m.integritycheck_id
    left join Priorities p on p.id = m.priority_id
    
    
    left join vNotesEx n on m.foreignid_id = n.foreignid_id and n.latest_foreign = 1
  where
    
    @include_closed = 1 or (n.is_open is null or n.is_open = 1)
    and c.active = 1
    
  order by
     P.RANK
    , c.check_name 
    , a.asset_id
    , coalesce(m.single_person,a.name_simple)
    
    
end


   
  drop table #missing
  drop table #a
  drop table #ae
  drop table #d
  drop table #v
  drop table #p
end
GO


--- FILE: ReportRunner\ReportRunner\SQL\Stored Proc UAM.dbo.ConsolidatedMissingDataTEST.sql ---
SET ANSI_NULLS ON;
GO
SET QUOTED_IDENTIFIER ON;
GO
ALTER proc [dbo].[ConsolidatedMissingDataTEST] @asset_id varchar(30) = null, @display_summary bit = 0, @detail_badger bit = 0, @include_closed bit = 1, @days_back int = null, @priority_level int = null
as
begin


  
  drop table if exists #missing
  drop table if exists #d
  drop table if exists #a
  drop table if exists #ae
  drop table if exists #v
  drop table if exists #p

 declare @threshold float = 0.0
 declare @start_date DATE
 declare @is_max bit = 0
 declare @hourago DATE
 
select @hourago = DATEADD(hh, -1, dbo.NYTime(GETDATE()))

if(@days_back IS NULL)
begin
select @start_date = '1/1/1990'
end
else
begin
select @start_date =DATEADD(day, -@days_back, dbo.TodayNY()) 
end

if(@priority_level IS NULL)
begin
select @priority_level  = 4
end

 select * into #a from vAssetsEx a where 1=2
 select * into #ae from vApplicantsEx where 1=2
 
 insert into #a select * from vAssetsEx a where ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id)
 if((select count(*) from #a) = 0 )
 begin
  alter table #a alter column address_full varchar(max) null
  insert into #a select * from vAssetsMaxEx a where ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id) 
  insert into #ae select * from vApplicantsMaxEx ae where (@asset_id is null or ae.asset_id = @asset_id)
  select @is_max = 1
 end
 else
 begin
  insert into #ae select * from vApplicantsEx ae where (@asset_id is null or ae.asset_id = @asset_id)
 end

 
 
 select * into #v from vValuations ae where (@asset_id is null or ae.asset_id = @asset_id)
 select * into #p from vPayoffs ae where (@asset_id is null or ae.asset_id = @asset_id)
 
 select d.asset_id,balance,rate,payment,d.lien_position,credit_limit,princ_payoff_amt,d.account_closed,account_open_date,a.secured_debt, sum(d.balance_calc) [balance_calc],d.debttype_id,l.name [lender_name] into #d from vDebt d join #a a on a.asset_id = d.asset_id left join Lenders l on l.id = d.lender_id where (@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id group by d.asset_id,balance,rate,payment,d.lien_position,credit_limit,princ_payoff_amt,balance_calc,a.secured_debt,d.account_closed,account_open_date,d.debttype_id,l.[name]
 

  create table #missing
  (
    asset_id varchar(30)
    , integritycheck_id int
    , single_person varchar(100)
    
    , [value] varchar(250)
    , priority_id int 
    , row_color varchar(30)
    , foreignid_id int
    , foreignidtype_id int
  )

  INSERT INTO #missing (asset_id,integritycheck_id,value) 
  select asset_id,2,credit_score from #a a where a.credit_score is null 

  INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 3 
     , cs.credit_score
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
        left join vCreditScores cs on ae.applicant_id = cs.applicant_id and cs.initial = 1
    where
        cs.credit_score is null    


  INSERT INTO #missing (asset_id,integritycheck_id,value)
  select
  a.asset_id
  , 97 
  , 'CR: ' + format(sum(ctl.balance/1000.0),'0') + 'k BADGER: ' + format(sum(a.secured_debt/1000.0),'0') + 'k P/O: ' + FORMAT(sum(isnull(d.princ_payoff_amt,0)),'0') + 'k'
  
  from
    vAssetApplicantSingle aas 
    join vCreditFiles crs on crs.applicant_id = aas.applicant_id and isnull(crs.applicant_co_id,'') = isnull(aas.applicant_co_id,'')
    join vCRTradelines ctl on ctl.creditfile_id = crs.creditfile_id and open_close = 'Open' and acct_type = 'Mortgage'
    join #a a on a.asset_id = aas.asset_id and (a.asset_id = @asset_id or @asset_id is null)
    left join #d d on d.asset_id = a.asset_id
    
 where
  crs.initial_api = 1
  
 group by 
  a.asset_id
  , crs.creditfile_id
  , a.name_simple
  , a.address_simple
  having
    sum(a.secured_debt)< sum(ctl.balance*.97)
  order by
    sum(a.secured_debt)-sum(ctl.balance)
    
    
    
  INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 51 
     , ae.last_name
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        (AE.last_name like '% Sr.' OR AE.last_name like '% Jr.' OR AE.last_name like '% III')
        
        
      INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 65 
     , ae.email
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        dbo.CheckValidEmail(ae.email) != 1
        
        
    INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 52 
     , FORMAT(ae.dob,'MM/dd/yyyy')
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        DATEPART(yy, ae.dob) <= 1900
        
    INSERT INTO #missing (asset_id,integritycheck_id,value)
    select 
      a.asset_id
     , 77 
     , convert(varchar(30),ae.dob)
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        age_at_origination_youngest <= 21
        
        INSERT INTO #missing (asset_id,integritycheck_id,value)
    select 
      a.asset_id
     , 96 
     , a.zip
      from 
        #a a
   
    where
        len(zip) != 5
        
        
        
    INSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 53 
     , convert(varchar(30),ae.full_name)
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        a.first_name like '% %' or a.last_name like '% %' or a.first_name like '%.%' or a.last_name like '%.%'

  iNSERT INTO #missing (asset_id,integritycheck_id,value,single_person)
  select 
      a.asset_id
     , 55 
     , convert(varchar(30),ae.full_name)
     , ae.full_name 
      from 
        #a a
        left join #ae ae on a.asset_id = ae.asset_id
    where
        a.first_name like '%.%'
        
  INSERT INTO #missing (asset_id,integritycheck_id) 
  select 
    a.asset_id
    , 4 
      from 
        #a a
      where
       a.closingagent_id is null
      order by
        effective_date asc

INSERT INTO #missing (asset_id,integritycheck_id) 
  select 
    a.asset_id
    , 92 
      from 
        #a a
      where
       a.credit_score < 550 and a.exchange_rate < 1.7
      order by
        effective_date asc
        
  INSERT INTO #missing (asset_id,integritycheck_id) 
  select 
    a.asset_id
    , 87 
      from 
        #a a
      where
       a.title_held_in_type_id is null
      order by
        effective_date asc
        
  INSERT INTO #missing (asset_id,integritycheck_id,single_person)
  select 
    ap.asset_id
    ,5 
    , ap.full_name
    
      from 
        #ae ap
        left join #a a on ap.asset_id = a.asset_id
      where
      ap.ssn_last4 is null
      and ((@asset_id is null and a.final_disposition_date is null) or a.asset_id = @asset_id)
    
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 6 
      from 
        #a a
    where
      a.doc_consent_of_spouse is null
    
  INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,7 
      from 
        #a a
    where
      a.origination_fee is null
      

  INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     
    select 
      a.asset_id
      ,54 
      ,a.cost_limit
      from 
        #a a
    where
      (a.cost_limit != .18 and a.cost_limit_basis!=A.INVESTMENT_PAYMENT)
      OR
      (a.cost_limit = .18 and a.cost_limit_basis!=a.investment_payment-a.origination_fee)
      
      
   INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     
    select 
      a.asset_id
      ,95 
      ,a.cost_limit
      from 
        #a a
    where 
    a.cost_limit_basis = a.investment_payment
   and a.lockout_months is not null
      
  INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     

  select
   a.asset_id
   , 66 
   , 'MTG: ' + format(d.balance,'0,###') + ' P/O: ' + format(p.payoff_final,'0,###')
    from 
      #a a 
      join #d d on d.asset_id = a.asset_id
      join #p p on d.asset_id = P.asset_id AND d.balance = p.payoff_final
    WHERE
    balance_calc != 0
      

  INSERT INTO #missing (asset_id,integritycheck_id,[value])  
    select
    p.asset_id
    , 67 
    , 'P/O: ' + p.account_name + ' - ' + format(p.payoff_final,'0,###') + 'k' + CASE WHEN d.lender_name is not null then ' vs Debt: ' + format(d.balance,'0,###') + 'k' else '' end
      from 
        #a a 
        join #p p on a.asset_id = P.asset_id
        left join #d d on d.asset_id = p.asset_id  and p.account_name = d.lender_name
      where
        (P.mortgage_debt = 0 OR P.MORTGAGE_DEBT IS NULL)
        and
        (

          (
          d.lender_name IS NOT NULL
          or
          (account_name like '%Funding%' or account_name like '%Mortgage%' or account_name like '%Loan%' or account_name like '%Funding%' or account_name like '%Bank%' or account_name like '%Credit Union%' or account_name like '% CU%'))
          
          or
          d.asset_id is not null
        )
      
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 20 
      from 
        #a a
    where
      a.max_proceeds is null
      

 
  INSERT INTO #missing (asset_id,integritycheck_id,[VALUE])     
    select 
      a.asset_id
      ,8 
      , CONVERT(VARCHAR(30),format(a.investment_payment-a.max_proceeds ,'0,000'))
      from 
        #a a
    where
      a.investment_payment-a.max_proceeds > 1.0
      
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,9 
      from 
        #a a
    where
      a.proceedsuse_id is null

   
    INSERT INTO #missing (asset_id,integritycheck_id,[value])     
    select 
      D.asset_id
      ,39 
      , format(balance_calc-secured_debt,'0,###')
      from 
        (select sum(balance_calc) [balance_calc],asset_id,min(secured_debt) [secured_debt] from #d s where s.account_closed is null group by asset_id) d 
        where
          ABS(CONVERT(int, balance_calc-secured_debt))>@threshold 
     
      
  
    
    INSERT INTO #missing (asset_id,integritycheck_id,value)     
    select 
      d.asset_id
      ,40 
      , format(balance-princ_payoff_amt,'0,###')
      from 
        #d d
    where
      (balance-princ_payoff_amt) < -@threshold 
    
   INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,10 
      from 
        #d a
    where
      a.rate >= .25 and a.account_closed is null
      
            
  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 36 
    from 
      #a a 
      left join #d c on a.asset_id = c.asset_id
    where
      c.rate is null and a.lien_position != 1 and (c.balance_calc > 1 or c.account_closed is null)
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 11 
      from 
        #a a
    where
      a.purchase_amount IS NULL
    
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 12 
      from 
        #a a
    where
      a.purchase_date IS NULL
      
          INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 13 
      from 
        #a a
    where
      a.term != 120
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 14 
      from 
        #d a
    where
      a.account_open_date is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 15 
      from 
        #a a
    where
      a.doc_maintenance_addendum is null

      
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 16 
      from 
        #a a
    where
      a.credit_score < 550 and a.dti is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 86 
      from 
        #a a
    where
      a.credit_score = 0 
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 17 
      from 
        #a a
    where
      a.dscr is null and a.is_rental = 1
   
    INSERT INTO #missing (asset_id,integritycheck_id,[value])     
    select 
      a.asset_id
      , 74 
      , a.apn
      from 
        #a a
    where
      a.apn in ('Principal Residence')

    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 18 
      from 
        #a a
    where
      a.dti > 1.0
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 19 
      from 
        #a a
    where
      a.legal_desc is null
      
      
        INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 21 
      from 
        #a a
    where
      a.legal_desc is not null and (charindex(a.county,a.legal_desc)=0 or charindex(a.county,a.legal_desc) is null)
    
            INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 49 
      from 
        #a a
    where
      (charindex('COUNTY',a.county)<>0)
      
     
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 22 
      from 
        #a a
    where
      a.folder_name_ups is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 23 
      from 
        #a a
    where
      a.propertycondition_id is null

    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 24 
      from 
        #a a
    where
      a.secured_debt is null
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 25 
      from 
        #a a
    where
      a.secured_debt = 0 and a.lien_position != 1
      
      
      INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 26 
      from 
        #a a
    where
      a.secured_debt >= starting_home_value
      
      
    INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 76 
      from 
        #a a
    where
      a.credit_score <= 550 and a.is_rental = 1
      
      
      
         INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 27 
      from 
        #a a
    where
      a.total_home_finance > a.total_home_finance_limit
     

        INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 28 
      from 
        #a a
    where
      a.propertytype_id is null

        INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 46 
      from 
        #a a
    where
      a.county in ('USA')
      
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      , 29 
      from 
        #a a
    where
      a.beds is null or a.baths is null or a.sqft is null
      

  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    d.asset_id
    
    
    , 30 
    
    from 
      #d d
        join #a a on a.asset_id = d.asset_id
    where
      
      (d.balance_calc != 0)
    group by
      d.asset_id
      , a.lien_position
    having
      count(*)+1 != a.lien_position
  
      

  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 31 
    from 
      #a a 
      left join #d c on a.asset_id = c.asset_id
    where
      c.asset_id is null and a.secured_debt != 0
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 38 
    from 
      #a a 
      left join #d d on a.asset_id = d.asset_id
    where
      
      d.debttype_id is null and a.secured_debt != 0 and d.account_closed is null
      

      
    INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 37 
    from 
      #a a 
      left join #d D on a.asset_id = D.asset_id
    where
      d.payment is null and a.secured_debt != 0 and d.account_closed is null
    
      
  INSERT INTO #missing (asset_id,integritycheck_id,[value])     
  select 
    a.asset_id
    
    
    , 57 
    , CONVERT(VARCHAR(30),format(a.starting_home_value/1000.0,'###k') + ' vs ' + format(v.value/1000.0,'###k') + ' (' + format((a.starting_home_value-v.value)/1000.0,'###k') + ' diff)') 
    from 
      #a a 
      join #v v on a.asset_id = v.asset_id
    where
      a.starting_home_value > v.[value]
      and v.valuationtype_id IN (21,22)
      
      
   INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id

    , 78 
    from 
      #a a 
      left join #v v on a.asset_id = v.asset_id and v.initial_uw = 1
    
      GROUP BY a.asset_id
      HAVING count(*) = 0 
      
      
      
      
      
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
  select 
    a.asset_id
    
    
    , 32 
    from 
      #a a 
      left join vInsurance c on a.asset_id = c.asset_id
    where
      c.asset_id is null
      
      
  INSERT INTO #missing (asset_id,integritycheck_id,[value])     
  select 
    a.asset_id
    
    
    , 41 
    , convert(varchar(30),cs.credit_score) + ' Deal vs ' + convert(varchar(30),cs.credit_score_calc) + ' Calc'
    from 
      #a a 
      left join vCreditScoreAsset cs on a.asset_id = cs.asset_id AND INITIAL = 1
    where
      cs.credit_score != credit_score_calc
      
  INSERT INTO #missing (asset_id,integritycheck_id)     
      SELECT 
     ae.asset_id
     , 33 
    
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  where
    ae.maritalstatus_id = 2
    
  GROUP by
    ae.asset_id
    , a.asset_id
    , ae.maritalstatus_id
    , a.doc_consent_of_spouse
  having
    count(*) = 1
    and doc_consent_of_spouse = 0
    
    
   INSERT INTO #missing (asset_id,integritycheck_id,[value])     
      SELECT 
     ae.asset_id
     , 71 
     , mailing_address_full
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  where
    mailing_address_full is not null and (mailing_address_1 is null or mailing_state is null or mailing_zip is null)
    
    
    
       INSERT INTO #missing (asset_id,integritycheck_id,[value])     
      SELECT 
     ae.asset_id
     , 73 
     , mailing_address_full + ' & ' + address_full
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  where
    mailing_address_1 IS not null and (mailing_address_1 = address_1)
    
    
    
    
  INSERT INTO #missing (asset_id,integritycheck_id)     
        SELECT 
     ae.asset_id
     , 50 
    
  from 
    #ae ae
    join #a a on a.asset_id = ae.asset_id
  
    
    
    
  GROUP by
    ae.asset_id
  having
    count(distinct(ae.ssn_last4)) != count(*)

   INSERT INTO #missing (asset_id,integritycheck_id,[value])     
    select 
      a.asset_id
     , 98 
	  , convert(varchar(30),uw.credit_score) + ' FICO & ' + format(a.total_home_finance_limit,'0.0%') + ' THFL'
      from 
        #a a
		join vUnderwriting uw on a.asset_id = uw.asset_id
    where
      a.total_home_finance_limit > .8  AND
	  (uw.credit_score > 499  AND uw.credit_score < 620)
   
   INSERT INTO #missing (asset_id,integritycheck_id,[value])  
   select 
      a.asset_id
     , 99 
	  , convert(varchar(30),uw.credit_score) + ' FICO & ' + format(a.total_home_finance_limit,'0.0%') + ' THFL'
      from 
        #a a
		join vUnderwriting uw on a.asset_id = uw.asset_id
    where
      a.total_home_finance_limit > .85  AND
	  (uw.credit_score > 619 AND uw.credit_score < 700)
     
     INSERT INTO #missing (asset_id,integritycheck_id,[value])  
      select 
      a.asset_id
     , 100 
	  , convert(varchar(30),uw.credit_score) + ' FICO & ' + format(a.total_home_finance_limit,'0.0%') + ' THFL'
      from 
        #a a
		join vUnderwriting uw on a.asset_id = uw.asset_id
    where
     a.total_home_finance_limit > .9  AND
	  uw.credit_score > 699
     
	INSERT INTO #missing (asset_id,integritycheck_id)     
    select 
      a.asset_id
      ,94 
      from 
        #a a
    where
      CAST(a.origination_fee_pct as decimal(2, 2)) != 0.03
      
         
    

INSERT INTO #missing (asset_id,integritycheck_id)
SELECT 
  a.asset_id
  
  
  , 35
  FROM 
  #A a 
  join vStateReqs s on (s.state = a.state)
  join Fields f on s.db_field = field
  where 
    s.statereqtype_id = 1
    and case when s.db_field = 'legal_desc_short' then a.legal_desc_short else null end is null

update m set priority_id= p.id from #missing m join IntegrityChecks ic on ic.id = m.integritycheck_id join Priorities p on p.id = ic.priority_id

update m set foreignid_id = f.foreignid_id from #missing m left join vForeignIds f on f.asset_id = m.asset_id and f.foreignidtype_id = 2 and m.integritycheck_id = f.foreign_id

if(@is_max=1)
  delete from #missing where integritycheck_id in (select id from IntegrityChecks where max_eligible = 0)


if @display_summary = 1
begin
  select
    count(*) [#]
    , i.check_name [exception]
  from
    #missing m
    left join #a a on a.asset_id = m.asset_id
    join vIntegrityChecks i on i.integritycheck_id = m.integritycheck_id
    left join vNotesEx n on m.foreignid_id = n.foreignid_id and n.latest_foreign = 1
    left join Priorities p on p.id = m.priority_id
  where
      a.effective_date > @start_date AND
      (@include_closed = 1 or (n.is_open is null or n.is_open = 1)
      and i.active = 1)
      and p.rank <=@priority_level 
  group by i.check_name
  order by count(*) desc
end

if(@detail_badger = 1)
begin
  select
    a.asset_id
    , a.effective_date
    , coalesce(m.single_person,a.name_simple) [name]
    
    , a.address_simple
    , c.check_name [exception]
    , m.value [value]
    , c.check_name
    
    , p.name_alt [priorityname_alt]
    , p.row_color
    , 'priorityname_alt' [col_color]
    , P.RANK
    , c.integritycheck_id
    , n.note
    
    
    
    
    , n.is_open
    , m.foreignid_id
    
    , m.foreignidtype_id
    , p.id [priority_id]
    , n.note_base_id
    , pr.last_name [processor_last_name]
    , s.last_name [sales_last_name]
    , u.last_name [underwriter_last_name]
    , cl.processor_id
    , cl.sales_id
    , cl.underwriter_id
    , n.is_open
    , c.qc_integritycheck_id
  from
    #missing m
    left join #a a on a.asset_id = m.asset_id
    left join vIntegrityChecks c on c.integritycheck_id = m.integritycheck_id
    left join Priorities p on p.id = m.priority_id
    
    left join vNotesEx n on m.foreignid_id = n.foreignid_id and n.latest_foreign = 1
    left join vClosingEx cl on cl.asset_id = a.asset_id
    left join vUsers pr on cl.processor_id = pr.monday_id
    left join vUsers s on cl.sales_id = s.monday_id
    left join vUsers u on cl.underwriter_id = u.monday_id
    
    where
      a.effective_date > @start_date AND
      (a.added_to_badger is null or a.added_to_badger < @hourago) AND 
      (@include_closed = 1 or (n.is_open is null or n.is_open = 1)
      and c.active = 1)
      AND p.rank <= @priority_level
  order by
    a.effective_date desc
    , P.RANK
    , coalesce(m.single_person,a.name_simple)
    , c.check_name
end
else
begin
  select
    p.name_alt [priority]
    , a.asset_id
    
    , coalesce(m.single_person,a.name_simple) [name]
    
    
    , c.check_name [exception]
    , m.value [value]
    
    
    
    
    
    
        , c.integritycheck_id
        , c.qc_integritycheck_id
    , n.note
    
    
    
    
    , n.is_open
    
    ,a.effective_date
    ,a.added_to_badger
  from
    #missing m
    left join #a a on a.asset_id = m.asset_id
    left join vIntegrityChecks c on c.integritycheck_id = m.integritycheck_id
    left join Priorities p on p.id = m.priority_id
    
    
    left join vNotesEx n on m.foreignid_id = n.foreignid_id and n.latest_foreign = 1
  where
   a.effective_date > @start_date AND
   (a.added_to_badger is null or a.added_to_badger < @hourago) AND 
    (@include_closed = 1 or (n.is_open is null or n.is_open = 1)
    and c.active = 1)
    AND p.rank <= @priority_level
  order by
     P.RANK
    , c.check_name 
    , a.asset_id
    , coalesce(m.single_person,a.name_simple)
    
    
end


   
  drop table #missing
  drop table #a
  drop table #ae
  drop table #d
  drop table #v
  drop table #p
end
GO


--- FILE: ReportRunner\ReportRunner\SQL\TerminatedSettlementRequests.sql ---
select a.max_id [MAX_ID],count(statement_date)[#_of_requests],min(statement_date)[first_request_date],max(statement_date)[final_request_date],max(a.final_disposition_date)[termination_date]
,DATEDIFF(day,min(statement_date),max(final_disposition_date))[days_between_initial]
,DATEDIFF(day,max(statement_date),max(final_disposition_date))[days_between_final]
,max(settlement_type) [settlement_type]
from SettlementRequests sr
join vAssetsEx a on sr.asset_id = a.asset_id where a.final_disposition_date is not null and sr.statement_date<a.final_disposition_date
group by a.max_id


--- FILE: ReportRunner\ReportRunner\SQL\TradeLineMapping.sql ---
drop table if exists #missing
drop table if exists #updates


declare @lastCredit datetime
declare @update bit = 1
declare @duplicateMappings bit = 0

 




declare @payment_threshold int = ISNULL(@input_payment_threshold,1000)
declare @balance_threshold int = ISNULL(@input_balance_threshold,5000)
declare @open_date_threshold int = ISNULL(@input_open_date_threshold,5)

select @lastCredit =  EOMONTH(max(asOf),-1) from dbo.CreditLoads cl where filename is not null


select d.*, a.effective_date, a.max_id, a.final_disposition_date, a.lien_position [asset_lien_position]
  into #missing
  from 
    vDebtEx d 
      join vAssets a on a.asset_id = d.asset_id     
    where 
      d.account_closed is null 
      and (d.cr_visible = 1 or d.cr_visible is null) 
      and (d.cr_reported = 1 or d.cr_reported is null) 
      and a.final_disposition_date is null
      and d.balance_calc != 0
      and d.craccount_id is null
      and a.lien_position > 1  
      and a.effective_date <= @lastCredit  
      and d.paid_off_at_origination <> 1

      
      
      
      and d.debt_type not in ('Solar Loan','Solar Lease','HUD 0%/Balloon')
      
    order by
      d.asset_id,d.lender_name




select 
  d.max_id
  , d.asset_id
  , d.effective_date
  , d.asset_lien_position [unlock_lien_position]
  , d.debt_type
  
  , d.lender_name [Badger.LenderName]
  , tradeLineMatch.match_lender_name  [TradeLine.Creditor]
  
  
  
  
      
  
  , d.balance [Badger.OriginationBalance]
  , tradeLineMatch.match_balance  [TradeLine.Balance]
  , d.balance_calc-tradeLineMatch.match_balance [BadgerTradeLineDiff.Balance]
  
  
  , d.payment [Badger.Payment]
  , tradeLineMatch.match_payment  [TradeLine.Payment]
  , d.payment-tradeLineMatch.match_payment [BadgerTradeLineDiff.Payment]

  
  , d.account_open_date [Badger.AccountOpenDate]
  , tradeLineMatch.match_dateopened  [TradeLine.AccountOpenDate]
  , DateDiff(DAY,d.account_open_date, tradeLineMatch.match_dateopened) [BadgerTradeLineDiff.AccountOpenDate] 
  , tradeLineMatch.proposed_craccount_id  [TradeLine.Proposed_CRAccountId]
  , d.debt_id [Badger.DebtId]
  , d.note [Badger.Note]
  , tradeLineMatch.match_note [Tradeline.Note]
  , tradeLineMatch.match_msg [Criteria]

  into #updates
  from 
  #missing d
    
    

    OUTER APPLY dbo.GetTradeLineMatch
      (
      d.asset_id
      ,d.payment
      ,d.balance
      ,d.account_open_date
      ,d.lender_name
      , @payment_threshold
      , @balance_threshold
      , @open_date_threshold
      ) as tradeLineMatch
      
  

  
    select CONCAT('[', SUM(case when u.[TradeLine.Proposed_CRAccountId] is null then 0 else 1 end),'] Proposed Mappings for [', COUNT(*), '] Unmapped Tradelines   |  Thresholds: [Payment +/- $',@payment_threshold, '] [Balance +/- $', @balance_threshold, '] [Account Open Date +/- ', @open_date_threshold,' Days]')  
    from #updates u

  
  select COUNT(*) [# Assets Unmapped]  
    ,SUM(case when u.[TradeLine.Proposed_CRAccountId] is null then 0 else 1 end) [# proposed mappings]
    from #updates u

  
  select @payment_threshold [Payment Threshold], @balance_threshold [Balance Threshold],  @open_date_threshold [Account Open Threshold]  

  
  select * from #missing 
  
  
  select @lastCredit [last credit] 
     
  
  
  
  select u.[TradeLine.Proposed_CRAccountId],count(*) [cr accounts mapped more than once]  
    from #updates u
    where u.[TradeLine.Proposed_CRAccountId] is not null
   group by u.[TradeLine.Proposed_CRAccountId]
   having count(*) >1  
   
  
  select @duplicateMappings [# of duplicate mappings] 
   
  
  select * from #updates t 

  
  select count(*) from Debt d join #updates t on d.id = t.[Badger.DebtId] where t.[TradeLine.Proposed_CRAccountId] is not null


  
  
  
  
  
   
drop table if exists #missing
drop table if exists #updates


--- FILE: ReportRunner\ReportRunner\SQL\TrustPilot.sql ---
drop table if exists #tmp
drop table if exists #TERMINATED


select
distinct
  a.asset_id
  , app.first_name
  , app.last_name
  , app.email
  , app.phone
  , a.effective_date
  
  
  ,convert(bit,case when pros.prospect_id is not null then 1 else 0 end) [matched_to_outreach]
  
  , pros.SOURCE
  , pros.campaign
  , a.final_disposition_date
  , datediff(d,a.effective_date,a.final_disposition_date) [days_outstanding]
  
  into #tmp
  from
    vAssetsEx a
    left join vApplicantsEx app on app.asset_id = a.asset_id and applicanttype_id = 1
    left join vClosing f on a.asset_id = f.asset_id
    left join vPipeline p on p.pipeline_id = f.pipeline_id
    left join OutreachOps o on p.internal_id = o.OPPORTUNITY_ID
    left join OutreachOppUserMap oum on oum.OPPORTUNITY_ID = o.OPPORTUNITY_ID
    left join vOutreachMapHack ph on (ph.[USER_ID] = oum.[USER_ID] or (oum.user_id is null and ph.EMAIL = a.email))
    left join OutreachPros pros on ph.prospect_id = pros.PROSPECT_ID
  
    
order by a.effective_date desc

select count(*) [count],source,campaign,sum(case when final_disposition_date is null then 1 else 0 end) [outstanding],sum(case when final_disposition_date is null then 0 else 1 end) [terminated], avg(case when final_disposition_date is not null then [days_outstanding] else null end) [avg_days_outstanding_for_terminated_deals] INTO #TERMINATED from #tmp group by source,campaign
SELECT * FROM #TERMINATED WHERE TERMINATED > 0 order by count desc
select * from #tmp order by effective_date desc

SELECT app.first_name,app.last_name,app.email,app.phone,t.campaign,a.final_disposition_date FROM vAssetsEx a join vApplicantsEx app on a.asset_id = app.asset_id and applicanttype_id = 1 left join #tmp t on t.asset_id = a.asset_id where a.final_disposition_date is not null order by a.final_disposition_date desc


drop table if exists #tmp
drop table if exists #TERMINATED


--- FILE: ReportRunner\ReportRunner\SQL\UAMDaily.sql ---
drop table if exists #tmp

select 
  owner
  , initiative
  , cadence
  , name
  , due_date
  , datediff(d,due_date,dbo.GetDateNY()) [days_of_failure] 
  into #tmp
  from 
    vUAMCal c 
  join @who u on u.item = c.owner 
  
  
select OWNER [hombre],initiative,NAME,DUE_DATE,DAYS_OF_FAILURE from #tmp where days_of_failure > @days_of_failure order by days_of_failure desc
if(@full_list = 1)
  select OWNER [hombre],initiative,NAME,DUE_DATE,DAYS_OF_FAILURE from #tmp where due_date > dbo.GetDateNY() order by days_of_failure desc

drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\uft1_certification_status.sql ---
DECLARE @v_Total_Collateral float
DECLARE @v_asofdate date, @v_asofdate_collateral float, @v_asofdate_collateral_total float

DROP TABLE IF EXISTS #TMP
DROP TABLE IF EXISTS #tmp_certification_forecast 

SELECT distinct ship.asset_id, ship.ship_date, ship.asof, 
	WSFSList.Certification_ID, (case when WSFSList.Certification_ID is null then 'Not Certified' else 'Certified' end) as certification_status, 
	pos.account, assets.investment_payment,  dbo.AddBdays(ship_date,2) as 'SLA_Certifcation_Date', 
	isnull(vFundings_New.funding_status, 'Not Funded') as funding_status, 
	vFundings_New.value_date as funding_date
INTO #TMP
from vCollatShipmentDetailEx ship
left join WSFS_List_Of_Loans WSFSList on WSFSList.Asset_ID = ship.asset_id
left join vPositions pos on pos.asset_id = ship.asset_id
left join vAssets assets on assets.asset_id = ship.asset_id
left join vFundings_New on vFundings_New.asset_id = ship.asset_id
where asof >='6/1/2023'
and shipped =1
and doc_custodian_name = 'wsfs'
and type = 'Digital'
and pos.account in ('UFT1')


select @v_Total_Collateral =sum(investment_payment) 
from #TMP

select 'Proir Day Close' as 'Label', dbo.AddBdays(dbo.TodayNY(),-1) as 'As_Of', convert(float,0.0) as additional_collateral, sum(investment_payment) as total_collateral 
into #tmp_certification_forecast
from #TMP where Certification_ID is not null
and SLA_Certifcation_Date < convert(date,dbo.AddBdays(dbo.TodayNY(),0))

select @v_asofdate_collateral = isnull(sum(investment_payment),0)
	from #tmp
	where Certification_ID is null
	and SLA_Certifcation_Date = convert(date,dbo.AddBdays(dbo.TodayNY(),0))

select @v_asofdate_collateral_total = isnull(total_collateral,0) from #tmp_certification_forecast

insert into #tmp_certification_forecast(Label, As_Of, additional_collateral, total_collateral)
select 'Today', dbo.AddBdays(dbo.TodayNY(),0), @v_asofdate_collateral, @v_asofdate_collateral +@v_asofdate_collateral_total

select @v_asofdate_collateral = isnull(sum(investment_payment),0)
	from #tmp
	where Certification_ID is null
	and SLA_Certifcation_Date = convert(date,dbo.AddBdays(dbo.TodayNY(),1))

select @v_asofdate_collateral_total = isnull(total_collateral,0) from #tmp_certification_forecast

insert into #tmp_certification_forecast(Label, As_Of, additional_collateral, total_collateral)
select 'Tomorrow', dbo.AddBdays(dbo.TodayNY(),1), @v_asofdate_collateral, @v_asofdate_collateral +@v_asofdate_collateral_total





select certification_status ,
  total,
  sum(case when funding_status ='Funded' then 1 else 0 end) as 'Funded',
  sum(case when funding_status ='Not Funded' then 1 else 0 end) as 'Not Funded'
from
(
  select count(*) over(partition by certification_status) total,
    funding_status,
    certification_status
  from #tmp
) d
group by certification_status, total
union all
select 'All',
  count(*),
  sum(case when funding_status ='Funded' then 1 else 0 end) as 'Funded',
  sum(case when funding_status ='Not Funded' then 1 else 0 end) as 'Not Funded'
from #tmp ;



with tmp_data as
(
	select 
		  certification_status
		, investment_payment as 'Total'
		, (case when trim(funding_status) = 'Funded' then investment_payment else 0 end) as 'Funded'
		,(case when trim(funding_status) ='Not Funded' then investment_payment else 0 end) as 'Not_Funded'
	from #TMP
)
select certification_status, sum(Total) as Total_$, sum(Funded) as Funded_$, sum(Not_Funded) as Not_Funded_$
	from tmp_data
	group by certification_status
union all 
select 'All', sum(Total) as Total, sum(Funded) as Funded, sum(Not_Funded) as Not_Funded
from tmp_data


select asset_id, funding_status, ship_date as 'ship_date_MM/dd/yyyy',  dbo.AddBdays(funding_date,2) as 'UFT1_Certifcation_Due_Date_MM/dd/yyyy', 
	funding_date, investment_payment
from #TMP
where funding_status = 'Funded'
and certification_status = 'Not Certified'
order by funding_date asc

DROP TABLE IF EXISTS #TMP
DROP TABLE IF EXISTS #tmp_certification_forecast


--- FILE: ReportRunner\ReportRunner\SQL\UnallocatedUAMWires.sql ---
select 
  b.jpminv_id
  , b.value_date
  , b.amount_cr [amount_|0,000.00|]
  , b.[description]
  , b.remark
  , p.*
  from 
    vJPMInvEx b
    left join vSettlementTransEx s on s.banktrans_id = b.jpminv_id
    left join vPartialPaymentTrans p on p.banktrans_id = b.jpminv_id
  where 
    b.account_number = 80018953081
    and b.amount_cr between 20000 and 700000
    and s.net_amount is null and p.partialpayment_id is null
    and b.[DESCRIPTION] not like '%REVERSAL%'
    and b.jpminv_id not in (300000118, 300001331, 300003282,300008516)


--- FILE: ReportRunner\ReportRunner\SQL\UnlockNotOnInsurance.sql ---
drop table if exists #tmp

select
  a.effective_date
  , a.asset_id
  , a.name_simple [name]
  , a.address_full [address]
  , i.unlock_insured
  into #tmp
  from
    vAssetsEx a
    left join vInsurance i on a.asset_id = i.asset_id
  where
    a.final_disposition_date is null
  
  select distinct asset_id,name,address,effective_date from #tmp where asset_id not in (select asset_id from #tmp where unlock_insured=1)


--- FILE: ReportRunner\ReportRunner\SQL\UnsentUSBankCollat.sql ---
select 
  a.max_id
  , a.name_simple
  , a.investment_payment
  , a.added_to_badger
  , a.effective_date 
  , c.funding_date

  , datediff(d,c.funding_date,GetDate()) [days_since_funding]
  from 
    vAssetsEx a 
    left join vCollatInvEx s on s.asset_id = a.asset_id 
    join vClosingEx c on c.asset_id = a.asset_id
  where 
    s.asset_id is null and a.final_disposition_date is null
    and
    (datediff(d,c.funding_date,GetDate()) >5)
  order by
    datediff(d,c.funding_date,GetDate()) desc


--- FILE: ReportRunner\ReportRunner\SQL\Unshipped_assets_digital.sql ---
select assets.asset_id, assets.effective_date, dbo.LastOwner(assets.asset_id), pos.account, datediff(DAY,assets.effective_date,dbo.TodayNY()) as Days_Since_Eff_Date,
assets.name_simple, assets.address_simple, ship_phys.ship_date as 'FSEA Physical Ship Date', added_to_badger, final_disposition_date, note
from vAssetsEx assets
left join vPositions pos on pos.asset_id = assets.asset_id
left join vCollatShipmentsEx ship_dig on ship_dig.asset_id =assets.asset_id  and ship_dig.collatshiptype_id =1
left join vCollatShipmentsEx ship_phys on ship_phys.asset_id =assets.asset_id  and ship_phys.collatshiptype_id =2 and ship_phys.doc_name = 'Forward Sale & Exchange Agreement'
left join vNotesEx notes on notes.asset_id = assets.asset_id and (notes.notestatus_id  = 1 or notes.notestatus_id  is null)
where ship_dig.ship_date is null
and assets.effective_date > DATEADD(m,-9, dbo.GetDateNY())
and pos.account is not null
and final_disposition_date is null
and added_to_badger<=dbo.TodayNY()
and assets.asset_id not in (select Asset_ID from WSFS_List_Of_Loans)
order by effective_date desc, asset_id


--- FILE: ReportRunner\ReportRunner\SQL\UpcomingAuctions.sql ---
DROP TABLE IF EXISTS #tmp 

select d.asset_id
, a.name_simple
, a.state
, d.date [auction_date]
, e.account_name
, e.vendor_name
, e.amount [bid_amount_|0,000.00|]
, e.status
into #tmp from vDefaultEventsEx d
left join vExpensesEx e on d.asset_id = e.asset_id and e.expensetype_id=9
join vAssetsEx a on d.asset_id = a.asset_id
where d.defaulteventtype_id=5 
order by auction_date



select * from #tmp where status is not null and auction_date>=dbo.TodayNY()
select asset_id, name_simple, state, auction_date from #tmp where status is null and auction_date>=dbo.TodayNY()
select * from #tmp where status is not null and auction_date between DATEADD(MONTH,-1,dbo.TodayNY()) and DATEADD(DAY,-1,dbo.TodayNY())


DROP TABLE #tmp


--- FILE: ReportRunner\ReportRunner\SQL\UpdatedSignETA.sql ---
select asset_id,customer_pipeline_label,net_wire_amt [net_wire_amt_|0,###.00|],estimated_signing,sign_eta_orig [estimated_signing_original],sub_stage[stage] from vClosingEx c where c.estimated_signing != c.sign_eta_orig and c.originated = 0 and funding_date is null and sub_stage not in ('Closed Lost')
select asset_id,customer_pipeline_label,net_wire_amt [net_wire_amt_|0,###.00|],funding_date,estimated_signing,sign_eta_orig [estimated_signing_original],sub_stage[stage] from vClosingEx c where c.estimated_signing != c.sign_eta_orig and c.originated = 0 and funding_date is NOT null and sub_stage not in ('Closed Lost')


--- FILE: ReportRunner\ReportRunner\SQL\UpdatedSignETANew.sql ---
select asset_id,customer_pipeline_label,net_wire_amt [net_wire_amt_|0,###.00|],estimated_signing,sign_eta_orig [estimated_signing_original],funding_date,group_name,datediff(d,estimated_signing,sign_eta_orig) [days_bumped_up] from vClosingEx c where c.estimated_signing != c.sign_eta_orig and c.originated = 0 and funding_date is null and c.group_name not in ('Lost','Paused Deals') and datediff(d,estimated_signing,sign_eta_orig) >= 2 and estimated_signing <= dbo.TodayNY()


--- FILE: ReportRunner\ReportRunner\SQL\UpdateUPSTrades.sql ---
DECLARE @ALL bit = 1

drop table if exists #tmp

  select 
    a.asset_id
    , a.investment_payment
    , 1 [account_id]
    , 'B' [buy_sell]
    , 0 [counterparty_id]
    , a.effective_date [trade_date]
    , a.effective_date [settle_date]
    , 100 [price]
  into #tmp
  from 
    vAssets a
    left join vCollatInv i  on i.asset_id = a.asset_id and i.latest = 1
    where 
      not exists(select * from vTrades t where t.asset_id = a.asset_id and is_unlock = 1 and t.is_journal = 1)
      and
      (
        (i.asset_id is null and @all = 1)
        or
        (i.asset_id is not null and @all = 0)
      )
  
select * from #tmp

insert into Trades (asset_id,oface,account_id,buy_sell,counterparty_id,trade_date,settle_date,price) select * from #tmp


drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\WireOutages.sql ---
select f.frbinv_id,transaction_date,f.amount,f.SUPPLEMENTARY_DETAILS from vFRBInvEx f left join vDealFundings c on f.frbinv_id = c.frbinv_id where f.TRANSACTION_DATE > '9/20/2022' and f.TRANSACTION_DESCRIPTION like '%CLEAREDGE%' and c.frbinv_id is null and f.ACCOUNT_NUMBER = 80009175797


select asset_id,customer_pipeline_label,effective_date,sub_stage,estimated_signing,investment_payment,net_wire_amt,net_funded,remaining_to_fund 
from vClosingEx 
where effective_date > '9/20/2022' 
and (remaining_to_fund != 0) 
and net_funded is not null 
and not (net_funded =0 and wire_count =2) 
and abs(remaining_to_fund)>.01


select asset_id,customer_pipeline_label,effective_date,sub_stage,estimated_signing,investment_payment,net_wire_amt,net_funded [net_funded_|0,000.00|],remaining_to_fund [remaining_to_fund_|0,000.00|] from vClosingEx where effective_date > '9/20/2022' and monday_originated = 1 and funded = 0


--- FILE: ReportRunner\ReportRunner\SQL\WrongUSBAssetID.sql ---
select
c.collateral_key
, c.borrower_name
, c.lnamount [investment_payment_$]
, c.address
, c.city
, c.state
, c.zip
, c.cert_status
from
  vCollatInv c
  where
    c.latest = 1
    and
    not exists (select * from vAssets a where a.asset_id = c.collateral_key)


--- FILE: ReportRunner\ReportRunner\SQL\WSFSCustody.sql ---
select t.trade_id
  ,a.max_id [asset_id]
  , a.effective_date
  , a.expiration_date [expiration_date]
  , a.apn [property_apn]
  , a.name_simple [property_owner]
  , a.occupancy_type [property_occupancy]
  , a.address_simple [property_address]
  , a.city [property_city]
  , a.state [property_state]
  , a.zip [property_zip]
  , a.starting_home_value
  , a.investment_payment
  , a.investment_pct
  , a.exchange_rate
  , a.unlock_pct
  , a.cost_limit [annualized_cost_limit]
  , a.total_home_finance_limit [home_finance_limit]
  , convert(bit,a.doc_consent_of_spouse) [doc_include_consent_of_spouse]
  , convert(bit,0) [doc_include_title_insurance]
  , convert(bit,1) [doc_include_title_report],t.net_proceeds into #tmp from vTrades t join vAssetsEx a on a.asset_id = t.asset_id 
    where t.settle_date = dbo.TodayNY()  
 
     and t.is_unlock = 0 and t.account_id = @account 
     and t.is_journal = 0
  
  select count(*) [#],sum(investment_payment) [total_investment_payment_$],sum(net_proceeds) [net_proceeds_$] from #tmp 
  
  select * from #tmp 
  
  drop table #tmp


--- FILE: ReportRunner\ReportRunner\SQL\wsfs_collater_status_sla.sql ---
declare @p_reportdate date
declare @p_asofdate varchar(20) = ''


declare @v_asofdate date

set @p_reportdate = dbo.TodayNY()

if isdate(@p_asofdate) =1
	set @v_asofdate =convert(datetime, @p_asofdate)
else
	select @v_asofdate = max(AsOfDate) from WSFS_Master_Schedule

declare @v_asset_id varchar(255)
declare @v_date_recieved datetime
declare @v_documenttype varchar(250)
declare @v_status varchar(250) 
declare @v_days_elapsed int
declare @v_days_sla int
declare @v_trade_id int
declare @v_settle_date datetime
declare @v_Forward_Sale_Agreement varchar(255)
declare @v_Performance_Deed varchar(255)
declare @v_Assignment_Of_Performance_Deed varchar(255)
declare @v_Title_Insurance_policy varchar(255)
declare @v_Asset_Count int
declare @v_Asset_Delivered int
declare @v_Asset_Intransit int
declare @v_Total_Documents int
declare @v_Within_SLA int
declare @v_NotWithIn_SLA int

set @v_days_sla = 45

drop table if exists #tmp

create table #tmp (asofdate date, asset_id varchar(255), trade_id int, settle_date date, date_recieved date, document varchar(250), doc_status varchar(250), days_elapsed int, days_sla int)

DECLARE WSFS_Master_Schedule_Exceptions_Cursor CURSOR FOR 
select wsfs_master.asset_id, t.trade_id, wsfs_master.Date_Recieved, Forward_Sale_Agreement, Performance_Deed, Assignment_Of_Performance_Deed, Title_Insurance_policy, t.settle_date
from vPositionsAll p , WSFS_Master_Schedule wsfs_master, WSFS_List_Of_Loans WSFS_Loans , vTradesex t
where p.account = @p_accountname
and p.asset_id = wsfs_master.Asset_ID
and wsfs_master.AsOfDate = @v_asofdate
and p.asset_id = WSFS_Loans .Asset_ID
and WSFS_Loans.trade_id = t.trade_id
and WSFS_Loans.Asset_ID = t.asset_id
and t.account = p.account

OPEN WSFS_Master_Schedule_Exceptions_Cursor 

fetch next from WSFS_Master_Schedule_Exceptions_Cursor into @v_asset_id,  @v_trade_id, @v_date_recieved, @v_Forward_Sale_Agreement, @v_Performance_Deed, 
	@v_Assignment_Of_Performance_Deed,@v_Title_Insurance_policy, @v_settle_date 

WHILE @@FETCH_STATUS = 0  
BEGIN  
	if isdate(@v_date_recieved) = 1
		set @v_days_elapsed = DATEDIFF(day, @v_settle_date, @v_date_recieved)
	else
		set @v_days_elapsed = DATEDIFF(day, @v_settle_date, @p_reportdate)

	
	set @v_status = 'Ok'
	if @v_Forward_Sale_Agreement is null set @v_status = 'Not Delivered'
	if lower(@v_Forward_Sale_Agreement) ='missing' set @v_status = 'Not Delivered'

	insert into #tmp (asofdate, asset_id, trade_id, date_recieved, settle_date, document, doc_status, days_elapsed, days_sla)
	values (@p_reportdate, @v_asset_id, @v_trade_id, @v_date_recieved, @v_settle_date, 'Forward Sale & Exchange Agreement', @v_status, @v_days_elapsed, @v_days_sla)

	
	set @v_status = 'Ok'
	if @v_Performance_Deed is null set @v_status = 'Not Delivered'
	if lower(@v_Performance_Deed) ='missing' set @v_status = 'Not Delivered'

	insert into #tmp (asofdate, asset_id, trade_id, date_recieved, settle_date, document, doc_status, days_elapsed, days_sla)
	values (@p_reportdate, @v_asset_id, @v_trade_id, @v_date_recieved, @v_settle_date, 'Performance Deed of Trust', @v_status, @v_days_elapsed, @v_days_sla)

	
	set @v_status = 'Ok'
	if @v_Assignment_Of_Performance_Deed is null set @v_status = 'Not Delivered'
	if lower(@v_Assignment_Of_Performance_Deed ) ='missing' set @v_status = 'Not Delivered'

	insert into #tmp (asofdate, asset_id, trade_id, date_recieved, settle_date, document, doc_status, days_elapsed, days_sla)
	values (@p_reportdate, @v_asset_id, @v_trade_id, @v_date_recieved, @v_settle_date, 'Assignment of Performance Mortgage', @v_status, @v_days_elapsed, @v_days_sla)

	
	
	
	

	
	

	fetch next from WSFS_Master_Schedule_Exceptions_Cursor into @v_asset_id,  @v_trade_id, @v_date_recieved, @v_Forward_Sale_Agreement, @v_Performance_Deed, 
		@v_Assignment_Of_Performance_Deed,@v_Title_Insurance_policy, @v_settle_date 
END

close WSFS_Master_Schedule_Exceptions_Cursor 
deallocate WSFS_Master_Schedule_Exceptions_Cursor 

drop table if exists #DeliveryStatusSummary
create table #DeliveryStatusSummary(Status varchar(250), Total_Documents int, Within_SLA int, NotWithIn_SLA int)

select @v_Total_Documents = count(*) from #tmp 
select @v_Within_SLA = count(*) from #tmp where days_elapsed <= days_sla
insert into #DeliveryStatusSummary(Status, Total_Documents, Within_SLA, NotWithIn_SLA)
values ('Total', @v_Total_Documents,  @v_Within_SLA, @v_Total_Documents- @v_Within_SLA)

select @v_Total_Documents = count(*) from #tmp where doc_status = 'Ok'
select @v_Within_SLA = count(*) from #tmp where doc_status = 'Ok' and days_elapsed <= days_sla
insert into #DeliveryStatusSummary(Status, Total_Documents, Within_SLA, NotWithIn_SLA)
values ('Delivered', @v_Total_Documents,  @v_Within_SLA, @v_Total_Documents- @v_Within_SLA)

select @v_Total_Documents = count(*) from #tmp where doc_status <> 'Ok'
select @v_Within_SLA = count(*) from #tmp where doc_status <> 'Ok' and days_elapsed <= days_sla
insert into #DeliveryStatusSummary(Status, Total_Documents, Within_SLA, NotWithIn_SLA)
values ('In Transit', @v_Total_Documents,  @v_Within_SLA, @v_Total_Documents- @v_Within_SLA)

select * from #DeliveryStatusSummary

delete from #DeliveryStatusSummary
drop table #DeliveryStatusSummary


drop table if exists #TradeStatusSummary

create table #TradeStatusSummary(trade_id int, settle_date  date, Total_Documents int, Within_SLA int, NotWithIn_SLA int)

insert into #TradeStatusSummary (trade_id, settle_date ) select trade_id, settle_date from #tmp group by trade_id, settle_date 

DECLARE TradeSummary_Cursor CURSOR FOR select trade_id from #TradeStatusSummary 

OPEN TradeSummary_Cursor 

fetch next from TradeSummary_Cursor  into @v_trade_id
WHILE @@FETCH_STATUS = 0  
	BEGIN  

	select @v_Total_Documents  = count(*) from #tmp where trade_id = @v_trade_id
	select @v_Within_SLA = count(*) from #tmp where days_elapsed <= days_sla and trade_id = @v_trade_id
	
	update #TradeStatusSummary set Total_Documents=@v_Total_Documents, Within_SLA = @v_Within_SLA , NotWithIn_SLA =@v_Total_Documents - @v_Within_SLA where trade_id = @v_trade_id
	

	fetch next from TradeSummary_Cursor  into @v_trade_id
	end


close TradeSummary_Cursor 
deallocate TradeSummary_Cursor 


select * from #TradeStatusSummary 
order by settle_date asc

drop table if exists #TradeStatusSummary 


select asofdate, #tmp.asset_id, trade_id, date_recieved, settle_date, document, doc_status, days_elapsed, days_sla
from #tmp
where doc_status <> 'Ok'
and days_elapsed > days_sla
order by days_elapsed desc

drop table if exists #tmp


--- FILE: ReportRunner\ReportRunner\SQL\wsfs_collater_status_ups.sql ---
DECLARE @v_Total_Collateral float
DECLARE @v_asofdate date, @v_asofdate_collateral float, @v_asofdate_collateral_total float

DROP TABLE IF EXISTS #TMP
DROP TABLE IF EXISTS #tmp_certification_forecast 

SELECT distinct ship.asset_id, ship.ship_date, ship.asof, WSFSList.Certification_ID, pos.account, assets.investment_payment,  dbo.AddBdays(ship_date,2) as 'SLA_Certifcation_Date', vFundings_New.funding_status
INTO #TMP
from vCollatShipmentDetailEx ship
left join WSFS_List_Of_Loans WSFSList on WSFSList.Asset_ID = ship.asset_id
left join vPositions pos on pos.asset_id = ship.asset_id
left join vAssets assets on assets.asset_id = ship.asset_id
left join vFundings_New on vFundings_New.asset_id = ship.asset_id
where asof >='6/1/2023'
and shipped =1
and doc_custodian_name = 'wsfs'
and type = 'Digital'
and pos.account in('UPS', 'UFT1')


select @v_Total_Collateral =sum(investment_payment) 
from #TMP

select 'Proir Day Close' as 'Label', dbo.AddBdays(dbo.TodayNY(),-1) as 'As_Of', convert(float,0.0) as additional_collateral, sum(investment_payment) as total_collateral 
into #tmp_certification_forecast
from #TMP where Certification_ID is not null
and SLA_Certifcation_Date < convert(date,dbo.AddBdays(dbo.TodayNY(),0))

select @v_asofdate_collateral = isnull(sum(investment_payment),0)
	from #tmp
	where Certification_ID is null
	and SLA_Certifcation_Date = convert(date,dbo.AddBdays(dbo.TodayNY(),0))

select @v_asofdate_collateral_total = isnull(total_collateral,0) from #tmp_certification_forecast

insert into #tmp_certification_forecast(Label, As_Of, additional_collateral, total_collateral)
select 'Today', dbo.AddBdays(dbo.TodayNY(),0), @v_asofdate_collateral, @v_asofdate_collateral +@v_asofdate_collateral_total

select @v_asofdate_collateral = isnull(sum(investment_payment),0)
	from #tmp
	where Certification_ID is null
	and SLA_Certifcation_Date = convert(date,dbo.AddBdays(dbo.TodayNY(),1))

select @v_asofdate_collateral_total = isnull(total_collateral,0) from #tmp_certification_forecast

insert into #tmp_certification_forecast(Label, As_Of, additional_collateral, total_collateral)
select 'Tomorrow', dbo.AddBdays(dbo.TodayNY(),1), @v_asofdate_collateral, @v_asofdate_collateral +@v_asofdate_collateral_total




select (case when Certification_ID is not null then 'Certified' else 'Not Certified' end) as 'Certification Status',
sum(investment_payment) as investment_payment
from #TMP
group by (case when Certification_ID is not null then 'Certified' else 'Not Certified' end)
union all 
select 'Total', @v_Total_Collateral



select Label, As_Of, additional_collateral, total_collateral
from #tmp_certification_forecast 



select asset_id, ship_date, asof, Certification_ID, investment_payment, funding_status
from #TMP
where Certification_ID is not null
order by ship_date



select asset_id, ship_date, asof, investment_payment, dbo.AddBdays(ship_date,2) as 'SLA Certifcation Date', funding_status
from #TMP
where Certification_ID is null
order by ship_date



DROP TABLE IF EXISTS #TMP
DROP TABLE IF EXISTS #tmp_certification_forecast


--- FILE: ReportRunner\ReportRunner\SQL\_ConsolidatedMissingData_DELETE.sql ---
drop table if exists #missing

create table #missing
(
  asset_id varchar(30)
  , single_person varchar(100)
  , [type] varchar(100)
  , [value] varchar(100)
)

INSERT INTO #missing (asset_id,type,value) 
select asset_id,'Deal Credit Score',credit_score from vAssetsEx a where a.credit_score is null

INSERT INTO #missing (asset_id,type,value,single_person)
select 
    a.asset_id
   , 'Individual Credit Score'
   , cs.credit_score
   , ae.full_name 
    from 
      vAssetsEx a
      left join vApplicantsEx ae on a.asset_id = ae.asset_id
      left join vCreditScores cs on ae.applicant_id = cs.applicant_id and cs.initial = 1
  where
      cs.credit_score is null    

INSERT INTO #missing (asset_id,type) 
select 
  a.asset_id
  , 'Closing Agent'
    from 
      vAssetsEx a
    where
     a.closingagent_id is null
    order by
      effective_date asc

INSERT INTO #missing (asset_id,type,single_person)
select 
  ap.asset_id
  , 'SSN #'
  , ap.full_name
  
    from 
      vApplicantsEx ap
      left join vAssetsEx a on ap.asset_id = a.asset_id
    where
     ap.ssn_last4 is null
  
 INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'Consent of Spouse'
    from 
      vAssetsEx a
  where
    a.doc_consent_of_spouse is null

 
 
  INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'Maintenance Addendum'
    from 
      vAssetsEx a
  where
    a.doc_maintenance_addendum is null
    
  INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'DSCR on Rental Property'
    from 
      vAssetsEx a
  where
    a.dscr is null and a.is_rental = 1
    
  INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'Property Condition'
    from 
      vAssetsEx a
  where
    a.propertycondition_id is null

  INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'Missing Secured Debt (check to mtg debt)'
    from 
      vAssetsEx a
  where
    a.secured_debt is null

      INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'Property Type'
    from 
      vAssetsEx a
  where
    a.propertytype_id is null
    
INSERT INTO #missing (asset_id,type)     
  select 
    a.asset_id
    , 'Property SQFT/Beds/Baths'
    from 
      vAssetsEx a
  where
    a.beds is null or a.baths is null or a.sqft is null
    

INSERT INTO #missing (asset_id,type)     
select 
  c.asset_id
  
  
  , 'Implied vs Stated Unlock Lien Position: ' + format(count(*)+1,'0') + ' vs ' + format(a.lien_position,'0')
  from 
    Debt c
      join vAssetsEx a on a.asset_id = c.asset_id
  where
    c.account_closed is null  
  group by
    c.asset_id
    , a.lien_position
  having
    count(*)+1 != a.lien_position


INSERT INTO #missing (asset_id,type)     
select 
  a.asset_id
  
  
  , 'No Mortgages Recorded (could own free/clear)'
  from 
    vAssetsEx a 
    left join Debt c on a.asset_id = c.asset_id
  where
    c.asset_id is null
    
INSERT INTO #missing (asset_id,type)     
select 
  a.asset_id
  
  
  , 'No Insurance Recorded'
  from 
    vAssetsEx a 
    left join vInsurance c on a.asset_id = c.asset_id
  where
    c.asset_id is null
    

INSERT INTO #missing (asset_id,type)     
    SELECT 
   ae.asset_id
   , 'Married, 1 Applicant, No Consent of Spouse'
  
from 
  vApplicantsEx ae
  join vAssets a on a.asset_id = ae.asset_id
where
  ae.maritalstatus_id = 2
  
GROUP by
  ae.asset_id
  , a.asset_id
  , ae.maritalstatus_id
  , a.doc_consent_of_spouse
having
  count(*) = 1
  and doc_consent_of_spouse = 0

select
  a.asset_id
  
  , coalesce(m.single_person,a.name_simple) [name]
  
  , a.address_simple
  , m.type [exception]
  , m.value [value]
  
from
  #missing m
  join vAssetsEx a on a.asset_id = m.asset_id
order by
  a.effective_date
  , coalesce(m.single_person,a.name_simple)
  , exception



 
drop table #missing


--- FILE: AccountSyncer\AccountSyncer\MondayHelper.cs ---
namespace AccountSyncer
{
    internal class MondayHelper
    {
    }
}


--- FILE: AccountSyncer\AccountSyncer\Program.cs ---
namespace AccountSyncer
{
    class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);

            string user = args["user"];
            string pass = args["pass"];
            string mail_profile = args["mailprofile"];
            string notify = args["notify"];
            string server = args["server"];
            bool force_monday = args.ContainsFlag("force_monday");
            int sleep = args.ArgIfAvailable<int>("sleep", 360).Value;

            string post_cmd = args.ContainsFlag("postcmd") ? args["postcmd"] : null;
            bool update_monday = args.ContainsFlag("updatemonday");

            int hours = args.ArgIfAvailable<int>("hours", 10).Value;

            DateTime stop_time = DateTime.Now.AddHours(hours);



            
            
            
            
            
            

            if (update_monday)
            {
                DoBankUpdates(user, pass, server, mail_profile, notify, post_cmd);
                
            }

            IWebDriver driver = new ChromeDriver();
            

            try
            {
                
                driver.Navigate().GoToUrl("https:

                
                driver.FindElement(By.Name("email")).SendKeys(user);
                driver.FindElement(By.Name("password")).SendKeys(pass);
                var loginBtn = driver.FindElement(By.ClassName("submitButton"));
                loginBtn.Click();

                while (DateTime.Now <= stop_time)
                {

                    WebDriverWait wait = new WebDriverWait(driver, new TimeSpan(0, 0, 60));
                    Console.WriteLine("Waiting for sidebar...");
                    wait.Until(ExpectedConditions.ElementIsVisible(By.Id("sidebar-navitem-accounts")));


                    
                    var accountButton = driver.FindElement(By.Id("sidebar-navitem-accounts"));
                    accountButton.Click();

                    
                    var syncBtn = driver.FindElement(By.XPath("
                    syncBtn.Click();

                    System.Console.WriteLine($"Processing Bank Transactions...");
                    bool updated_something = DoBankUpdates(user,pass,server,mail_profile,notify,post_cmd);
                    System.Console.WriteLine($"Sleeping: {sleep} sec. ({DateTime.Now:H:mm tt)}");
                    System.Threading.Thread.Sleep(3000);

                    
                    System.Threading.Thread.Sleep(sleep * 1000);


                    if (updated_something && update_monday)
                    {
                        
                        
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error occured:{ex.Message}");
                UtilsLib.Error.SendDefaultError(ex, "Account Syncer",null,null);
            }
            finally
            {
                
                Thread.Sleep(30000);
                
                driver.Close();
                driver.Quit();
            }
        }

        public static bool DoBankUpdates(string user,string pass,string server,string mail_profile,string notify,string post_cmd)
        {
            BankLib.Loader l = new BankLib.Loader(user, pass);
            bool updated_something = l.StartLoad(server, mail_profile, notify, post_cmd);
            
            return updated_something;
        }
        
        
        
        
        
    }
}


--- FILE: AccountSyncer\AccountSyncer\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("AccountSyncer")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("AccountSyncer")]
[assembly: AssemblyCopyright("Copyright ©  2021")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("10e22723-4104-478e-af44-866308d76ae7")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: AccountSyncer\ConsoleApp1\Program.cs ---
namespace AccountSyncer
{
    class Program
    {
        static void Main(string[] args)
        {
            IWebDriver driver = new ChromeDriver();
            try
            {
                
                driver.Navigate().GoToUrl("https:

                
                driver.FindElement(By.Name("email")).SendKeys("EMAIL");
                driver.FindElement(By.Name("password")).SendKeys("PASSWORD");
                var loginBtn = driver.FindElement(By.ClassName("submitButton"));
                loginBtn.Click();

                
                var accountButton = driver.FindElement(By.Id("sidebar-navitem-accounts"));
                accountButton.Click();

                
                var syncBtn = driver.FindElement(By.XPath("
                syncBtn.Click();


                
                Thread.Sleep(10000);
                
            }
            catch(Exception ex)
            {
                Console.WriteLine($"Error occured:{ex.Message}");
            }
            finally
            {
                
                driver.Close();
                driver.Quit();
            }

        }
    }
}


--- FILE: MondaySync\Program.cs ---
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace MondayTest
{
    class Monda
    {
        static void Main(string[] arg)
        {
            

            CommandLineArgs args = new CommandLineArgs(arg);
            string mailprofile = null;
            string notify = null;
            
            int? throttle = null;
            bool sync = false;
            string force_str = args.ArgIfAvailableNotNull<string>("force", null);
            string config = args["config"];
            string dbtable = args.ArgIfAvailableNotNull<string>("dbtable", config);
            string postsqlcmd = args.ArgIfAvailableNotNull<string>("postsqlcmd", null);
            long[] force = null;
            if(null != force_str)
            {
                force = force_str.Split(',').Select(n => System.Convert.ToInt64(n)).ToArray();
            }
            string server = args["server"];

            MondayLib.MondayHelper.Results results = new MondayLib.MondayHelper.Results();
            
            {
                string api_key = args["api_key"];
                long board = args.ArgIfAvailable<long>("board", 0).Value;
                
                

                mailprofile = args["mailprofile"];
                notify = args["notify"];
                if (args.ContainsFlag("throttle"))
                    throttle = args.ArgIfAvailableNotNull<int>("throttle", 0);
                sync = args.ContainsFlag("sync");

                
                MondayLib.MondayHelper ms = new MondayLib.MondayHelper(board, api_key, throttle);

                if (config == "Pipeline")
                {
                    ms.AddItemMap("name", "name");
                    ms.AddColumnMap("sub_stage", "status3");
                    ms.AddColumnMap("investment_payment", "numbers");
                    ms.AddColumnMap("probability", "numbers0");
                    ms.AddColumnMap("estimated_signing", "date0");
                    ms.AddColumnMap("exception", "exception3");
                    ms.AddColumnMap("internal_id", "text");
                    ms.AddColumnMap("investor", "investor");
                    
                    ms.AddColumnMap("first_contact", "date5");
                    ms.AddColumnMap("sharepoint_link", "link_1");
                    ms.AddColumnMap("scheduled_signing", "date_18");

                    ms.AddColumnMap("sales_id", "people");
                    ms.AddColumnMap("underwriter_id", "people6");
                    ms.AddColumnMap("processor_id", "people0");
                    ms.AddColumnMap("partner_account_id", "connect_boards58");
                    ms.AddColumnMap("partner_account_txt", "connect_boards58");
                    ms.AddColumnMap("opp_source_id", "connect_boards");
                    ms.AddColumnMap("opp_source_txt", "connect_boards");
                    ms.AddColumnMap("max_text", "link7");
                    ms.AddColumnMap("fast_track", "status74");
                    ms.AddColumnMap("loss_notes", "dropdown7");
                    ms.AddColumnMap("loss_date", "date7");
                    ms.AddColumnMap("loss_reason", "status5");
                    ms.AddColumnMap("vrd", "date09");
                }
                else if (config == "Watchlist")
                {
                    ms.AddColumnMap("connected_pulse_id", "connect_boards");
                    ms.AddColumnMap("status", "status");
                    ms.AddColumnMap("ticket_type", "status_1");
                    ms.AddColumnMap("support_id", "person");
                    ms.AddColumnMap("create_date", "creation_log");
                    ms.AddColumnMap("pull_date", "date");
                    
                    ms.AddColumnMap("uam_comments", "text");
                }
                else if (config == "UAMCal")
                {
                    ms.AddColumnMap("owner_id", "person");
                    ms.AddColumnMap("status", "status");
                    ms.AddColumnMap("due_date", "date4");
                    ms.AddColumnMap("initiative", "status_19");
                    ms.AddColumnMap("cadence", "status_1");
                    
                }
                else if (config == "ServicingQueue")
                {
                    ms.AddColumnMap("pipeline_id", "connect_boards");
                    ms.AddColumnMap("status", "status");
                    ms.AddColumnMap("ticket_type", "status_1");
                    ms.AddColumnMap("waiting_on", "status_17");
                    ms.AddColumnMap("owner_id", "person");
                    ms.AddColumnMap("target_close", "date");
                    ms.AddColumnMap("asset_id", "text");
                    ms.AddColumnMap("created_on", "creation_log");
                    ms.AddColumnMap("primary_contact", "text8");
                }
                else if (config == "Draws")
                {
                    ms.AddColumnMap("status_nomura", "status_1");
                    ms.AddColumnMap("status", "mirror42");
                    ms.AddColumnMap("draw_num", "mirror4");
                    ms.AddColumnMap("request_type", "mirror05");
                    ms.AddColumnMap("address", "mirror0");
                    ms.AddColumnMap("paid_to", "mirror405");
                    ms.AddColumnMap("draw_amount", "mirror7");
                    ms.AddColumnMap("inspection_report", "mirror04");
                    ms.AddColumnMap("request_date", "mirror47");
                    ms.AddColumnMap("draw_report", "mirror2");
                    ms.AddColumnMap("additional_docs", "mirror5");
                    ms.AddColumnMap("fund_date", "mirror40");
                    ms.AddColumnMap("requested_by", "mirror48");
                    ms.AddColumnMap("requestor", "mirror24");
                    ms.AddColumnMap("requestor_email", "mirror6");
                    ms.AddColumnMap("sg_approver", "mirror83");
                    ms.AddColumnMap("request_reviewed_raw", "mirror03");
                    ms.AddColumnMap("trade_date", "mirror88");
                    ms.AddColumnMap("sg_approval_date", "mirror1");
                    ms.AddColumnMap("reimbursement_date", "mirror52");
                    ms.AddColumnMap("sg_deal", "mirror46");
                    ms.AddColumnMap("connected_board_id", "link_to_housemax___draws0");
                    ms.AddColumnMap("connected_pulse_id", "link_to_housemax___draws0");
                    ms.AddColumnMap("funding_type", "mirror");
                }
                else if (config == "Alphaflow")
                {
                    ms.AddColumnMap("status", "status");
                    ms.AddColumnMap("draw_num", "numbers");
                    ms.AddColumnMap("request_type", "dropdown");
                    ms.AddColumnMap("address", "address");
                    ms.AddColumnMap("paid_to", "date2");
                    ms.AddColumnMap("draw_amount", "numbers8");
                    ms.AddColumnMap("inspection_report", "file");
                    ms.AddColumnMap("request_date", "date_1");
                    ms.AddColumnMap("draw_report", "files");
                    ms.AddColumnMap("additional_docs", "dup__of_draw_report");
                    ms.AddColumnMap("fund_date", "date5");
                    ms.AddColumnMap("requested_by", "people");
                    ms.AddColumnMap("requestor", "dropdown5");
                    ms.AddColumnMap("requestor_email", "text6");
                    ms.AddColumnMap("sg_approver", "person");
                    ms.AddColumnMap("request_reviewed_raw", "check");
                    ms.AddColumnMap("trade_date", "date4");
                    ms.AddColumnMap("sg_approval_date", "date");
                    ms.AddColumnMap("reimbursement_date", "date3");
                    ms.AddColumnMap("sg_deal", "sg_deal");
                    ms.AddColumnMap("sg_notes", "text1");
                }
                if (config == "UAMCal")
                {
                    

                    
                    
                    

                    
                }

                if (null != force)
                {
                    
                    
                    ETA eta = new ETA(force.Length, Console.WriteLine);
                    foreach (long i in force)
                    {
                        
                        ms.ForceDoAllUpdate(server, dbtable, i);

                        eta.IncrementAndReport();
                        System.Threading.Thread.Sleep(15000);
                    }
                }
                if (sync)
                    results = ms.Sync(server, dbtable);


            }
            
            
            
            


            if(true)
            {
                
                
            }

            if(null != postsqlcmd)
            {
                Query q = new Query(postsqlcmd, server);
                q.Execute();
            }
            if (null != mailprofile)
            {
                if (results.inserted != 0 || results.updated != 0)
                {
                    Mail m = new Mail(mailprofile);
                    
                }
            }

            
            
        }
    }
}


--- FILE: MondaySync\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("MondayTest")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("MondayTest")]
[assembly: AssemblyCopyright("Copyright ©  2021")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("c84da04b-5ac2-44a2-9f8e-3c5f7a297616")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: MondaySyncer\MondaySyncer\Program.cs ---
namespace MondaySyncer
{
    internal class Program
    {
        static void Main(string[] arg)
        {

            CommandLineArgs args = new CommandLineArgs(arg);
            string user = args["user"];
            string pass = args["pass"];
            string mail_profile = args["mailprofile"];
            string notify = args["notify"];
            string server = args["server"];
            int sleep = System.Convert.ToInt32(args["sleep"]);


            List<int> pipelines = BadgerLib.Closing.GetNeededMondayUpdates(server);

            BankLib.MondayHelper.UpdatePipeline(pipelines);
        }
    }
}


--- FILE: MondaySyncer\MondaySyncer\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("MondaySyncer")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("MondaySyncer")]
[assembly: AssemblyCopyright("Copyright ©  2021")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("aa3e4630-2f22-40dd-82e1-efec1af55b4a")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: DBSync\DBSync\clsSyncStatus.cs ---
namespace DBSync
{
    internal class clsSyncStatusrec
    {
        private int _Id;
        private DateTime _CurrentDay;
        private DateTime _LastUpdate;
        private string _SyncName;
        private string _SourceName;
        private string _DestName;
        private DateTime _SyncStart;
        private DateTime _SyncEnd;
        private int _SourceRowCount;
        private int _DestRowCount;
        private string _SyncStatus;
        private bool _UpdateStatusInDB;

        public bool UpdateStatusInDB { get { return _UpdateStatusInDB; } set { _UpdateStatusInDB = value; } } 

        public clsSyncStatusrec (DateTime CurrentDay, string SyncName, string SourceName, string DestName, bool UpdateStatusInDB=true)
        {
            _CurrentDay = CurrentDay;
            _SyncName = SyncName;
            _SourceName = SourceName.Replace("'", "''");
            _DestName = DestName;
            _UpdateStatusInDB= UpdateStatusInDB;
        }

        public void SyncStatus_Start(string BadgerServer)
        {
            DateTime ts = DateTime.Now;

            string SqlStr_Insert = "insert into Status_SnowFlake_Sync(CurrentDay, LastUpdate, SyncName, SourceName, DestName, SyncStart, SyncStatus) values (";
            SqlStr_Insert += "'" + _CurrentDay.ToShortDateString() + "'";
            SqlStr_Insert += ", '" + ts.ToString() + "'";
            SqlStr_Insert += ", '" + _SyncName + "'";
            if (_SourceName.Length>255)
                SqlStr_Insert += ", '" + _SourceName.Substring(0,244) + "'";
            else
                SqlStr_Insert += ", '" + _SourceName+ "'";
            if (_DestName.Length>255)
                SqlStr_Insert += ", '" + _DestName.Substring(0, 244) + "'";
            else
                SqlStr_Insert += ", '" + _DestName+ "'";
            SqlStr_Insert += ", '" + ts.ToString() + "'";
            SqlStr_Insert += ", 'Starting');";
            Query q = new Query(SqlStr_Insert, BadgerServer);
            if (_UpdateStatusInDB)
            {
                q.Execute();
            }

            string SqlStr_GetID = "select max(id) as 'SyncID' from Status_SnowFlake_Sync where CurrentDay =";
            SqlStr_GetID += "'" + _CurrentDay.ToShortDateString() + "'";
            SqlStr_GetID += "and lastUpdate='" + ts.ToString() + "'";
            q.SetSQL(SqlStr_GetID);

            if (_UpdateStatusInDB)
            {
                _Id = q.ExecuteSingle<int>("SyncID");
            }
        }

        public void SyncStatus_GotSource(string BadgerServer, int SourceRowCount)
        {
            DateTime ts = DateTime.Now;
            _SourceRowCount = SourceRowCount;

            string SqlStr_Update = "Update Status_SnowFlake_Sync ";
            SqlStr_Update += " set SourceRowCount = " + _SourceRowCount.ToString("#0");
            SqlStr_Update += " , SyncStatus = 'Got Source Data'";
            SqlStr_Update += " , lastUpdate ='" + ts.ToString() + "'";
            SqlStr_Update += " where id = " + _Id.ToString("#0") + ";";

            if (_UpdateStatusInDB)
            {
                Query q = new Query(SqlStr_Update, BadgerServer);
                q.Execute();
            }
        }
        public void SyncStatus_LoadedDestination(string BadgerServer, int DestRowCount)
        {
            DateTime ts = DateTime.Now;
            _DestRowCount = DestRowCount;

            string SqlStr_Update = "Update Status_SnowFlake_Sync ";
            SqlStr_Update += "set DestRowCount = " + _DestRowCount.ToString("#0");
            SqlStr_Update += " , SyncStatus = 'Loaded Destination Data'";
            SqlStr_Update += " , lastUpdate ='" + ts.ToString() + "'";
            SqlStr_Update += " where id = " + _Id.ToString("#0") + ";";
            if (_UpdateStatusInDB)
            {
                Query q = new Query(SqlStr_Update, BadgerServer);
                q.Execute();
            }

        }
        public void SyncStatus_End(string BadgerServer)
        {
            DateTime ts = DateTime.Now;
            string Status = "";
            if (_DestRowCount == _SourceRowCount)
                Status = "Database load OK";
            else
                Status = "Error row count mismatch";


            string SqlStr_Update = "Update Status_SnowFlake_Sync ";
            SqlStr_Update += " set SyncStatus = '"+Status+"'";
            SqlStr_Update += " , SyncEnd ='" + ts.ToString() + "'";
            SqlStr_Update += " where id = " + _Id.ToString("#0") + ";";

            if (_UpdateStatusInDB)
            {
                Query q = new Query(SqlStr_Update, BadgerServer);
                q.Execute();
            }

        }

    }
}


--- FILE: DBSync\DBSync\Program.cs ---
using static System.Net.Mime.MediaTypeNames;
namespace DBSync
{
    class Program
    {
        private static readonly ILog log = LogManager.GetLogger(typeof(Program));

        static void Main(string[] arg)
        {
            XmlConfigurator.Configure(new FileInfo("log4net.config"));
            log.Info("Application started.");

            CommandLineArgs args = new CommandLineArgs(arg);
            
            string env = args.ContainsFlag("env") ? args["env"] : "PROD";
            CommonInterfaces.Constants.SetEnvironment(CommonInterfaces.Constants.GetEnvironment(env));
            
            UtilsLib.Dates.XDateTime d = new Dates.XDateTime(DateTime.Today);
            string from = args["from"];
            string to = args["to"];
            string send_mail_address = null;
            string mail_profile = args["mailprofile"];

            if (args.ContainsFlag("mail"))
                send_mail_address = args["mail"];

            DateTime asOf = d.PreviousBusinessDay();

            if (args.ContainsFlag("asof"))
                asOf = System.Convert.ToDateTime(args["asOf"].Replace("'", ""));

            if (args.ContainsFlag("dashboardCheck"))
            {
                updateSyncStatus(from, to);
                return;
            }
            else
            {
                log.Info("Hello World!");
                log.Info("mail to: " + args["mail"]);
                log.Info("Dest table: " + args["destTable"]);
            }


            if (args.ContainsFlag("IntraDay"))
            {
                log.Info("IntraDay: " + args["IntraDay"]);
                string stop_time = "23:00";
                if (args.ContainsFlag("StopTime")) 
                    stop_time = args["StopTime"];
                DoIntraDay(from, to, send_mail_address, mail_profile, stop_time);
            }
            else
            {

                DateTime end = asOf;
                string srcsql = args["sourcesql"];
                string destTable = args["destTable"];
                bool bulk = args.ContainsFlag("bulk");
                string postsql = args.ContainsFlag("postsql") ? args["postsql"] : null;
                string syncname = args.ContainsFlag("syncname") ? args["syncname"] : null;

                if (args.ContainsFlag("newSync"))
                {
                    string updateParamName = args["latstUpdatedParam"];

                    string formattedDate;
                    try
                    {
                        formattedDate = getMostRecentSQLRecord(updateParamName, destTable, to);
                    }
                    catch
                    {
                        formattedDate = "01/01/1900";
                    }


                    
                    if (!srcsql.ToLower().Contains("where"))
                        srcsql += " WHERE 1=1";

                    
                    if (args.ContainsFlag("lookbackTimeframe"))
                    {
                        int days = Int32.Parse(args["lookbackTimeframe"]);
                        DateTime pullDate = DateTime.Now.AddDays(days * -1);
                        formattedDate = pullDate.ToString("MM/dd/yyyy");
                    }

                    
                    if (args.ContainsFlag("startUpdateDate"))
                        formattedDate = args["startUpdateDate"];

                    
                    srcsql += " and " + updateParamName + " >'" + formattedDate + "'";
                    log.Info("MODIFIED SQL: " + srcsql);

                    
                    if (args.ContainsFlag("stopUpdateDate"))
                    {
                        srcsql += " and " + updateParamName + " <'" + args["stopUpdateDate"] + "'";
                        log.Info("MODIFIED SQL WITH STOP UPDATE DATE: " + srcsql);
                    }
                }

                Nullable<int> sleep = null;
                if (args.ContainsFlag("sleep"))
                    sleep = System.Convert.ToInt32(args["sleep"]) * 1000;

                if (args.ContainsFlag("backfill"))
                {
                    asOf = System.Convert.ToDateTime(args["start"]);
                    end = System.Convert.ToDateTime(args["end"]);
                }
                DateTime next = asOf;
                UtilsLib.Dates.XDateTime loop = new Dates.XDateTime(next);
                do
                {

                    if (args.ContainsFlag("newSync"))
                    {
                        NewDoSync(from, to, srcsql, destTable, next, send_mail_address, postsql, syncname, mail_profile, args.ContainsFlag("ignoreDeletes"));
                    } else{
                        DoSync(from, to, args["clearDestSql"], srcsql, destTable, bulk, next, send_mail_address, postsql, syncname, mail_profile);
                    }
                    loop.AddBusinessDays(1);
                    next = loop.Date;
                    if (null != sleep)
                    {
                        log.Info("Sleeping: " + sleep / 1000);
                        System.Threading.Thread.Sleep(sleep.Value);
                    }
                } while (next < end);
            }

            if (args.ContainsFlag("debug"))
            {
                System.Threading.Thread.Sleep(100000);
            }

        }


        public static void PrintDataTable(DataTable table)
        {
            
            foreach (DataColumn column in table.Columns)
            {
                Console.Write(column.ColumnName + "\t");
            }
            Console.WriteLine();

            
            foreach (DataRow row in table.Rows)
            {
                foreach (var item in row.ItemArray)
                {
                    Console.Write(item + "\t");
                }
                Console.WriteLine();
            }
        }
        public static string getMostRecentSQLRecord(string updateParamName, string destTable, string to)
        {
            log.Info("SELECT TOP 1 " + updateParamName + " FROM " + destTable + " ORDER BY " + updateParamName + " desc");
            log.Info("To: " + to);
            Query q = new Query("SELECT TOP 1 " + updateParamName + " FROM " + destTable + " ORDER BY " + updateParamName + " desc", to);
            DataTable res = q.ExecuteTable();
            DataRow newestRecord = res.Rows[0];

            DateTime pullDate = (DateTime)newestRecord[updateParamName];
            string formattedDate = pullDate.AddHours(-4).ToString("yyyy-MM-dd HH:mm:ss.fff") + " -0400";
            
            return formattedDate;
        }
        public static string getMostRecentSnowflakeRecord(string srcsql, String updateParamName, DateTime asOf, string from)
        {
            srcsql += " ORDER BY " + updateParamName + " desc LIMIT 1";
            DataTable tbl = GetSourceData(from, srcsql, asOf);
            DataRow newestRecord = tbl.Rows[0];
            DateTimeOffset datetimeOffset = (DateTimeOffset)newestRecord[updateParamName];

            DateTime pullDate = datetimeOffset.DateTime;
            string formattedDate = pullDate.AddHours(-4).ToString("yyyy-MM-dd HH:mm:ss.fff") + " -0400";

            return formattedDate;
        }
        public static void updateSyncStatus(string snowflakeDb, string sqlDB)
        {
            string Max_API_Table_Status_Snowflake = @"
                SELECT 'API_ADDRESS' AS TABLENAME, COUNT(*) AS ROW_COUNT, MAX(MODIFIED_AT) AS MODIFIED_AT_DATE FROM RAW.fivetran_max_app_prod_public.API_ADDRESS
                UNION ALL SELECT 'API_Application', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_Application
                UNION ALL SELECT 'API_APPLICATION_CREDIT_REPORTS', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM RAW.fivetran_max_app_prod_public.API_APPLICATION_CREDIT_REPORTS
                UNION ALL SELECT 'API_APPLICATIONEXCEPTION', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONEXCEPTION
                UNION ALL SELECT 'API_APPLICATIONPARTY', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONPARTY
                UNION ALL SELECT 'API_APPLICATIONPROFILE', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONPROFILE
                UNION ALL SELECT 'API_APPLICATIONPROFILE_CREDIT_REPORTS', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONPROFILE_CREDIT_REPORTS
                UNION ALL SELECT 'API_ASSET', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_ASSET
                UNION ALL SELECT 'API_CreditReport', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM RAW.fivetran_max_app_prod_public.API_CreditReport
                UNION ALL SELECT 'API_DEALTEAM', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_DEALTEAM
                UNION ALL SELECT 'API_Expense', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_Expense WHERE IE_ISSUE_DATE >= '2019-01-01' OR IE_ISSUE_DATE IS NULL AND DELETED_AT IS NULL AND AMOUNT <> 0
                UNION ALL SELECT 'API_HOI', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_HOI
                UNION ALL SELECT 'API_INCOME', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_INCOME
                UNION ALL SELECT 'API_OFFER', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_OFFER
                UNION ALL SELECT 'api_overrides', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.api_overrides
                UNION ALL SELECT 'API_PARTY', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_PARTY
                UNION ALL SELECT 'API_PROFILE', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_PROFILE
                UNION ALL SELECT 'API_Property', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_Property WHERE AQUIRED_ON >= '1902-01-01' OR AQUIRED_ON IS NULL
                UNION ALL SELECT 'API_TITLEREPORT', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_TITLEREPORT
                UNION ALL SELECT 'API_TRADELINE', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_TRADELINE
                UNION ALL SELECT 'API_USEOFPROCEEDS', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_USEOFPROCEEDS
                UNION ALL SELECT 'API_USERINCOME', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_USERINCOME
                UNION ALL SELECT 'API_VALUATION', COUNT(*), MAX(MODIFIED_AT) FROM RAW.fivetran_max_app_prod_public.API_VALUATION
                UNION ALL SELECT 'AUTH_USER', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM RAW.fivetran_max_app_prod_public.AUTH_USER
            ";

            Query q = new Query(Max_API_Table_Status_Snowflake, snowflakeDb);
            DataTable SnowFlake_dt = q.ExecuteTable();

            PrintDataTable(SnowFlake_dt);

            Console.WriteLine();
            Console.WriteLine("***");
            Console.WriteLine();

            string Max_API_Table_Status_Badger = @"
                DROP TABLE IF EXISTS #tmp;

                CREATE TABLE #tmp (
                    TableName VARCHAR(1024),
                    Row_Count INT,
                    MODIFIED_AT DATETIME2
                );

                INSERT INTO #tmp 
                SELECT 'API_ADDRESS', COUNT(*), MAX(MODIFIED_AT) FROM API_ADDRESS;

                INSERT INTO #tmp 
                SELECT 'API_Application', COUNT(*), MAX(MODIFIED_AT) FROM API_Application;

                INSERT INTO #tmp 
                SELECT 'API_APPLICATION_CREDIT_REPORTS', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM API_APPLICATION_CREDIT_REPORTS;

                INSERT INTO #tmp 
                SELECT 'API_APPLICATIONEXCEPTION', COUNT(*), MAX(MODIFIED_AT) FROM API_APPLICATIONEXCEPTION;

                INSERT INTO #tmp 
                SELECT 'API_APPLICATIONPARTY', COUNT(*), MAX(MODIFIED_AT) FROM API_APPLICATIONPARTY;

                INSERT INTO #tmp 
                SELECT 'API_APPLICATIONPROFILE', COUNT(*), MAX(MODIFIED_AT) FROM API_APPLICATIONPROFILE;

                INSERT INTO #tmp 
                SELECT 'API_APPLICATIONPROFILE_CREDIT_REPORTS', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM API_APPLICATIONPROFILE_CREDIT_REPORTS;

                INSERT INTO #tmp 
                SELECT 'API_ASSET', COUNT(*), MAX(MODIFIED_AT) FROM API_ASSET;

                INSERT INTO #tmp 
                SELECT 'API_CreditReport', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM API_CreditReport;

                INSERT INTO #tmp 
                SELECT 'API_DEALTEAM', COUNT(*), MAX(MODIFIED_AT) FROM API_DEALTEAM;

                INSERT INTO #tmp 
                SELECT 'API_Expense', COUNT(*), MAX(MODIFIED_AT) FROM API_Expense;

                INSERT INTO #tmp 
                SELECT 'API_HOI', COUNT(*), MAX(MODIFIED_AT) FROM API_HOI;

                INSERT INTO #tmp 
                SELECT 'API_HOI_TEST', COUNT(*), MAX(MODIFIED_AT) FROM API_HOI_TEST;

                INSERT INTO #tmp 
                SELECT 'API_INCOME', COUNT(*), MAX(MODIFIED_AT) FROM API_INCOME;

                INSERT INTO #tmp 
                SELECT 'API_OFFER', COUNT(*), MAX(MODIFIED_AT) FROM API_OFFER;

                INSERT INTO #tmp 
                SELECT 'api_overrides', COUNT(*), MAX(MODIFIED_AT) FROM api_overrides;

                INSERT INTO #tmp 
                SELECT 'API_PARTY', COUNT(*), MAX(MODIFIED_AT) FROM API_PARTY;

                INSERT INTO #tmp 
                SELECT 'API_PROFILE', COUNT(*), MAX(MODIFIED_AT) FROM API_PROFILE;

                INSERT INTO #tmp 
                SELECT 'API_Property', COUNT(*), MAX(MODIFIED_AT) FROM API_Property;

                INSERT INTO #tmp 
                SELECT 'API_TITLEREPORT', COUNT(*), MAX(MODIFIED_AT) FROM API_TITLEREPORT;

                INSERT INTO #tmp 
                SELECT 'API_TRADELINE', COUNT(*), MAX(MODIFIED_AT) FROM API_TRADELINE;

                INSERT INTO #tmp 
                SELECT 'API_USEOFPROCEEDS', COUNT(*), MAX(MODIFIED_AT) FROM API_USEOFPROCEEDS;

                INSERT INTO #tmp 
                SELECT 'API_USERINCOME', COUNT(*), MAX(MODIFIED_AT) FROM API_USERINCOME;

                INSERT INTO #tmp 
                SELECT 'API_VALUATION', COUNT(*), MAX(MODIFIED_AT) FROM API_VALUATION;

                INSERT INTO #tmp 
                SELECT 'AUTH_USER', COUNT(*), MAX(_FIVETRAN_SYNCED) FROM AUTH_USER;

                INSERT INTO #tmp 
                SELECT 'DOC_DRAWN', COUNT(*), NULL FROM DOC_DRAWN;

                SELECT * FROM #tmp;

                DROP TABLE IF EXISTS #tmp;
            ";

            Query q2 = new Query(Max_API_Table_Status_Badger, sqlDB);
            DataTable Sql_dt = q2.ExecuteTable();

            PrintDataTable(Sql_dt);
        } 

        public static void DoIntraDay(string from, string to, string send_mail_address, string mail_profile, string stop_time)
        {
            log.Info("Running IntraDay");
            string MsgBody = "", syncname = "Max Application Status ";
            DateTime ts = new DateTime();
            string asOf = "";
            Nullable<int> sleep = 300000;
            sleep = 30000;
            

            TimeSpan end_of_day = TimeSpan.Parse(stop_time);
            ts = DateTime.Now;
            UtilsLib.Mail m = new Mail(mail_profile);
            int ChangeCount, LastRowCount =0 ;
            while (ts.TimeOfDay < end_of_day)
            {
                ChangeCount = 0;
                asOf = ts.ToShortDateString() + " : " + ts.ToShortTimeString();
                MsgBody = "Update Time : "+asOf+System.Environment.NewLine;
                DataTable dt = new DataTable();
                dt = MaxLib.Utils.GetMaxApplicationStateChangesForToday(from);
                log.Info("[" + asOf + "] Updates Found " );
                dt = MaxLib.Utils.UpdateBadgerApplicationState_new(dt, to);
                DataView dv = new DataView(dt);
                dv.RowFilter ="HAS_CHANGED = 'YES'";
                dv.Sort = "APPLICATION_STATE";
                
                log.Info("New Application State Changes");
                MsgBody += System.Environment.NewLine + string.Format("New Application State Changes {0}", dv.Count) + System.Environment.NewLine;
                MsgBody += System.Environment.NewLine + "Application ID\t\tExternal ID\tApplication State Change";

                if (dv.Count ==0)
                    MsgBody += System.Environment.NewLine + '\t'+string.Format("*** No new changes ***") +System.Environment.NewLine;

                foreach (DataRowView row in dv)
                {
                    log.Info(row["ID"].ToString() + '\t' + row["EXTERNAL_ID"].ToString() + System.Environment.NewLine + "\t Previous Application State : " + row["APPLICATION_STATE_PRIOR"].ToString() + System.Environment.NewLine + "\t New Application State : " + row["APPLICATION_STATE"].ToString());
                    MsgBody += System.Environment.NewLine + row["ID"].ToString() + "\t\t" + row["EXTERNAL_ID"].ToString() + '\t' + row["APPLICATION_STATE_PRIOR"].ToString() + "\t --> \t" + row["APPLICATION_STATE"].ToString() +'\t'+ row["NAME"].ToString() + System.Environment.NewLine;
                    ChangeCount++;
                }

                dv.RowFilter = "HAS_CHANGED = 'NO'";
                log.Info("Previous Application State Changes");
                MsgBody += System.Environment.NewLine + string.Format("Previous Application State Changes {0}",dv.Count) + System.Environment.NewLine;
                MsgBody += System.Environment.NewLine + "Application ID\t\tExternal ID\tCurrent Application State ";
                foreach (DataRowView row in dv)
                {
                    log.Info(row["ID"].ToString() + '\t' + row["EXTERNAL_ID"].ToString() + System.Environment.NewLine + "\t Current Application State : " + row["APPLICATION_STATE"].ToString() + System.Environment.NewLine);
                    MsgBody += System.Environment.NewLine + row["ID"].ToString() + "\t\t" + row["EXTERNAL_ID"].ToString() +'\t'+ row["APPLICATION_STATE"].ToString()+'\t'+ row["NAME"].ToString();
                }

                string subject = String.Format("[{2:M/d/yyyy}] - {3} Sync - {0} new update(s) : {1} updates today", ChangeCount,dt.Rows.Count, asOf, syncname);
                if ((ChangeCount>0) || (LastRowCount != dt.Rows.Count))
                    m.SendSMTPMail(send_mail_address, null, null, subject, MsgBody, null, false, true, "badger@unlock.com", System.Net.Mail.MailPriority.High);
                
                

                log.Info("Sleeping (min): " + (sleep / 1000) / 60);
                System.Threading.Thread.Sleep(sleep.Value);
                ts = DateTime.Now;
                LastRowCount = dt.Rows.Count;
            }

            ts = DateTime.Now;
            asOf = ts.ToShortDateString() + " : " + ts.ToShortTimeString();
            m.SendSMTPMail(send_mail_address, null, null, syncname+" Done @" + asOf, MsgBody, null, false, true, "badger@unlock.com");
            log.Info("Done @"+ asOf);


        }
        public static void ReportMemoryUsage(string MemoryMsg)
        {

            float memory_float = (float)GC.GetTotalMemory(false);
            memory_float = memory_float / 1024;
            string ConsoleMessage = string.Format("{0} : {1}", MemoryMsg, memory_float.ToString("#,##"));
            log.Info("");
            log.Info(ConsoleMessage);
            log.Info("");

        }

        public static void ExecuteListInChunks(List<string> chunkList, string to)
        {
            var chunks = chunkList.SplitIntoChunks<string>(500);
            ETA eta = new ETA(chunks.Count, log.Info);

            foreach (var chunk in chunks)
            {
                string bulk_statements = String.Join(Environment.NewLine, chunk.Where(n => !n.Contains("System.Byte[]")).ToList());
                log.Info(bulk_statements);
                Query q = new Query(bulk_statements, to);
                q.Execute();
                eta.IncrementAndReport();
            }
        }
        static string GetErrorDetails(Exception ex)
        {
            
            string exceptionMessage = $"Exception Message: {ex.Message}{Environment.NewLine}";
            
            

            
            string pattern = @"\b\d{9}\b|\b\d{3}-\d{2}-\d{4}\b";
            
            exceptionMessage = Regex.Replace(exceptionMessage, pattern, "***-**-****");

            return exceptionMessage;
        }
        public static void NewDoSync(string from, string to, string srcsql, string destTable, DateTime asOf, string send_mail_address, string postSql, string syncname, string mail_profile, bool ignore_deletes)
        {
            log.Info("NewDoSync( " + from + ", " + to + ", " + srcsql + ", " + destTable + ", , " + send_mail_address + ", " + postSql + ", " + syncname + ", " + mail_profile + ", " + ignore_deletes + ")");
            
            

            log.Info("Processing Date: " + asOf.ToString("MM/dd/yyyy"));
            log.Info("Start Time " + DateTime.Now.ToShortTimeString());
            log.Info("Grabbing Data from: " + from.ToUpper());

            log.Info("***");
            ReportMemoryUsage("Memory Used Start");

            DataTable tbl = GetSourceData(from, srcsql, asOf);

            ReportMemoryUsage("Memory Used Got Data");

            int count = 0;

            List<string> delete_statements = GetClearStatements(tbl, destTable);
            List<string> insert_statements = GetSourceData_NOT_BULK_New(tbl, destTable);
            log.Info("Grabbed " + insert_statements.Count + " rows.");
            
            
            ReportMemoryUsage("Memory Used Generated SQL");


            try
            {
                if (!ignore_deletes)
                {
                    ExecuteListInChunks(delete_statements, to);
                    log.Info("Executed Deletes");
                }
                try
                {
                    ExecuteListInChunks(insert_statements, to);
                    log.Info("Executed Insert");
                }
                catch (Exception ex)
                {
                    SlackLib.SClient client = new SlackLib.SClient();
                    string errorDetails = GetErrorDetails(ex);
                    client.SendMessage(SClient.RECIPIENT.badger_growls, "*INSERTS FAILED ON TABLE* " + destTable + "\n*Error Details:*\n" + errorDetails, SClient.SEVERITY.severe);
                    return;
                }
            }
            catch (Exception ex)
            {
                SlackLib.SClient client = new SlackLib.SClient();
                string errorDetails = GetErrorDetails(ex);
                client.SendMessage(SClient.RECIPIENT.badger_growls, "*DELETES FAILED ON TABLE* " + destTable + "\n*Error Details:*\n"+errorDetails, SClient.SEVERITY.severe);
                return;
            }

            ReportMemoryUsage("Memory Used Transferred Data");

            
            if (!String.IsNullOrEmpty(postSql))
            {
                Query q = new Query(postSql, to);
                q.Execute();
            }

            if (!String.IsNullOrEmpty(send_mail_address))
            {
                string from_mail = "dbsync@unlock.com";
                UtilsLib.Mail m = new Mail(mail_profile);

                if (String.IsNullOrEmpty(syncname))
                    syncname = "UNKNOWN";
                string subject = String.Format("[{1:M/d/yyyy}] - {2} Sync Complete - {0}", count, asOf, syncname);
                m.SendSMTPMail(send_mail_address, null, null, subject, null, null, false, true, from_mail);
            }
            log.Info("End Time " + DateTime.Now.ToShortTimeString());
        }

            public static void DoSync(string from,string to, string clearDestSql, string srcsql, string destTable, bool bulk, DateTime asOf,string send_mail_address,string postSql,string syncname,string mail_profile)
        {
            clsSyncStatusrec SyncStatusrec = new clsSyncStatusrec(asOf, "MAX Update", srcsql, destTable,true);
            SyncStatusrec.SyncStatus_Start(to);

            log.Info("Processing Date: " + asOf.ToString("MM/dd/yyyy"));
            log.Info("Start Time " + DateTime.Now.ToShortTimeString());
            log.Info("Grabbing Data from: " + from.ToUpper());

            log.Info("***");
            ReportMemoryUsage("Memory Used Start");

             DataTable tbl = GetSourceData(from, srcsql, asOf);
            
            
            

            ReportMemoryUsage("Memory Used Got Data");

            ClearDest(to, clearDestSql, asOf);
            int count = 0;
            if (bulk)
            {
                List<Query> insert_statements = GetSourceData_BULK(from,to, destTable, srcsql, asOf);
                log.Info("Grabbed " + insert_statements.Count + " rows.");
                SyncStatusrec.SyncStatus_GotSource(to, insert_statements.Count);
                ReportMemoryUsage("Memory Used Generated SQL");

                
                
                
                
                
                

                
                
                
                
                
                

                TransferData(to, insert_statements, log.Info, bulk);
                ReportMemoryUsage("Memory Used Transferred Data");

                count = insert_statements.Count;
                SyncStatusrec.SyncStatus_LoadedDestination(to, count);
            }
            else
            {

                List<string> insert_statements = GetSourceData_NOT_BULK(from, destTable, srcsql, asOf);
                log.Info("Grabbed " + insert_statements.Count + " rows.");
                SyncStatusrec.SyncStatus_GotSource(to, insert_statements.Count);
                ReportMemoryUsage("Memory Used Generated SQL");

                var chunks = insert_statements.SplitIntoChunks<string>(500);
                ETA eta = new ETA(chunks.Count, log.Info);

                foreach (var chunk in chunks)
                {
                    string bulk_statements = String.Join(Environment.NewLine, chunk.Where(n => !n.Contains("System.Byte[]")).ToList());
                    Query q = new Query(bulk_statements, to);
                    q.Execute();
                    eta.IncrementAndReport();
                }

                ReportMemoryUsage("Memory Used Transferred Data");

                
                
                
                
                
                
                
                
                
                
                

            }

            SyncStatusrec.SyncStatus_End(to);
            if (!String.IsNullOrEmpty(postSql))
            {
                Query q = new Query(postSql, to);
                q.Execute();
            }

            if (!String.IsNullOrEmpty(send_mail_address))
            {
                string from_mail = "dbsync@unlock.com";
                
                UtilsLib.Mail m = new Mail(mail_profile);

                if (String.IsNullOrEmpty(syncname))
                    syncname = "UNKNOWN";
                string subject = String.Format("[{1:M/d/yyyy}] - {2} Sync Complete - {0}", count, asOf, syncname);
                m.SendSMTPMail(send_mail_address, null, null, subject, null, null, false, true, from_mail);
            }
            log.Info("End Time " + DateTime.Now.ToShortTimeString());



        }

        public static void TransferData(string to, List<Query> sqls, IWriter writer,bool bulk)
        {
            ETA eta = new ETA(sqls.Count, writer);
            if (!bulk)
            {
                foreach (Query q in sqls)
                {
                    
                    

                    

                
                
                
                }
            }
            else
            {
                if (null != writer)
                    writer("Beginning Bulk Load...");
                
                sqls.ForEach(n => n.SetConnection(to));
                Query.BulkExecute(sqls);
                
                
                
                
                
                
                if (null != writer)
                    writer("End Bulk Load...");
            }
        }

        public static void ClearDest(string server,string cleardestsql,DateTime asOf)
        {
            Query q = new Query(cleardestsql, server);
            q.AddParameter("@asOf", asOf);
            q.ApplyCommonVariables();
            q.Execute();
        }

        public static List<Query>  GetSourceData_BULK(string sourceDB, string destDB, string destTable, string sql, DateTime asOf)
        {
            Query q = new Query(sql, sourceDB);
            q.AddParameter("@asOf", asOf);
            q.ApplyCommonVariables();
            DataTable tbl = q.ExecuteTable();
            List<Query> insert_statements = Database.DBUtils.GenerateInsertStatements(destTable, tbl, true).inserts_all;
            return insert_statements;
        }

        public static List<string> GetSourceData_NOT_BULK_New(DataTable tbl, string destTable)
        {
            List<string> insert_statements = Database.DBUtils.GenerateInsertStatements(destTable, tbl, true, true).inserts_raw_dog;
            return insert_statements;
        }

        public static List<string> GetSourceData_NOT_BULK(string server, string destTable, string sql, DateTime asOf)
        {
            Query q = new Query(sql, server);
            q.AddParameter("@asOf", asOf);
            q.ApplyCommonVariables();
            DataTable tbl = q.ExecuteTable();
            List<string> insert_statements = Database.DBUtils.GenerateInsertStatements(destTable, tbl, true, true).inserts_raw_dog;
            return insert_statements;
        }

        public static List<String> GetClearStatements(DataTable tbl, string destTable)
        {
            List<string> delete_statements = new List<string>();

            foreach (DataRow row in tbl.Rows)
            {
                delete_statements.Add("delete from " + destTable + " where ID = " + row["ID"] + ";");
                
            }
            return delete_statements;
        }

        public static DataTable GetSourceData(string server,string sql, DateTime asOf)
        {
            Query q = new Query(sql, server);
            q.AddParameter("@asOf", asOf);
            q.ApplyCommonVariables();
            DataTable tbl = q.ExecuteTable();
            return tbl;
        }
    }
}


--- FILE: DBSync\DBSync\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("DBSync")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("DBSync")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2017")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("379633f3-a958-445c-99b1-be2a9365cacc")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BBGDestClear.sql ---
delete from Trading..BBG_TRADE_CURRENT where cast(UPDATE_TIMESTAMP as date) = @asOf


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BBGHistDestClear.sql ---
delete from Trading..BBG_TRADE_HISTORY where cast(UPDATE_TIMESTAMP as date) = @asOf


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BBGHistSrc.sql ---
select * from dbEnterpriseHub..BBG_TRADE_HISTORY WHERE cast(UPDATE_TIMESTAMP as date) = @asOf


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BBGPost.sql ---
insert into BBGDataQueue (cusip,note) 
 select distinct cusip_number,'BBG Trade Import' 
    from 
    BBG_TRADE_CURRENT b 
      where not exists (select * from Assets a where a.cusip = b.cusip_number) and cusip_number is not null and cusip_number not like '.%'
      and not exists (select * from BBGDataQueue bdq where bdq.cusip = b.cusip_number)
      and not exists (select * from BBGDataFail bdq where bdq.cusip_or_ticker = b.cusip_number)
	  


insert into KaneraiLoads (asOf,cusip,loaded,source)
select distinct trade_date,t.cusip,0,'Trade'
  from 
    vTradesUnsafe t 
  join Assets a on a.ticker = t.ticker
  left join KaneraiLoads kl on a.cusip = kl.cusip and t.trade_date = kl.asOf
  where
    a.product_id = 2
    and kl.loaded is null
    and t.trade_date >= dateadd(m,-3,GetDate())
	and a.collat_type not like '%CRE'


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BBGSrc.sql ---
select * from dbEnterpriseHub..BBG_TRADE_CURRENT WHERE cast(UPDATE_TIMESTAMP as date) = @asOf


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BetaDestClear.sql ---
delete from Trading..BetaHistory where processingTradeDate = @asOf


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BetaSecurityDestClear.sql ---
delete from Trading..BetaSecurity


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BetaSecurityPost.sql ---
select top 1 * from Trading.dbo.BetaSecurity

update c set c.cusip=null from Trading.dbo.BetaSecurity c where c.cusip = '         '


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BetaSecuritySrc.sql ---
select *  from dbWarehouse01.[dbo].tblSecurity p


--- FILE: DBSync\DBSync\SQL\ARCHIVE\BetaSrc.sql ---
select *  from [dbBulkImport].[dbo].[tblRit_pos_HISTORY] p where p.processingtradedate = @asOf and p.acct_no in (5251,5258,5249,5253,5254,5268,5266,5272,5274,5264,5288,5272,5266,5160,5172,5180,5230,5235,5240,5245,5250,5262,5310,5350,5370,5380,5480,5490,5495,5496,5319,5246,5238,5263,5264,5221,5222,5223,5224,5225,5226,5227,5228,5229,5247,5173,5491,5492,5493,5351,5267,5174,5268,5261,5269,5375,5376,5271,5273,5485,5281,5282,5283,5284,5285,5286,5211,5258,5212,5287,5274,5232,5289)


--- FILE: DBSync\DBSync\SQL\ARCHIVE\TOMS_DestClear.sql ---
delete from Trading..TOMS WHERE positionDate = @asOf


--- FILE: DBSync\DBSync\SQL\ARCHIVE\TOMS_Post.sql ---
insert into KaneraiLoads (cusip,source,asOf) 
select t.cusip,'TOMs Feed',t.PositionDate FROM TOMS t left join Assets a on t.cusip=a.cusip left join Kanerai k on a.ticker = k.ticker and k.update_time >= dateadd(d,-7,getdate()) left join KaneraiLoads kl on t.cusip=kl.cusip and kl.asOf = t.PositionDate where TraderCode in ('5274') and positionDate = dbo.PreviousBday(GetDate()) and PositionTimeHH24 = 17 AND k.ticker is null and kl.asOf is null


--- FILE: DBSync\DBSync\SQL\ARCHIVE\TOMS_Src.sql ---
select * from BBG.Position_Mart WHERE positionDate = @asOf


--- FILE: DBSync\DBSync\SQL\Max_API_Table_Status_Badger.sql ---
drop table if exists #tmp

create table #tmp (TableName varchar(1024), Row_Count int, MODIFIED_AT datetime2)

insert into #tmp SELECT 'API_ADDRESS', count(*), max(MODIFIED_AT) FROM API_ADDRESS
insert into #tmp SELECT 'API_Application', count(*), max(MODIFIED_AT) FROM API_Application
insert into #tmp SELECT 'API_APPLICATION_CREDIT_REPORTS', count(*), '' FROM API_APPLICATION_CREDIT_REPORTS
insert into #tmp SELECT 'API_APPLICATIONEXCEPTION', count(*), max(MODIFIED_AT) FROM API_APPLICATIONEXCEPTION
insert into #tmp SELECT 'API_APPLICATIONPARTY', count(*), max(MODIFIED_AT) FROM API_APPLICATIONPARTY
insert into #tmp SELECT 'API_APPLICATIONPROFILE', count(*), max(MODIFIED_AT) FROM API_APPLICATIONPROFILE
insert into #tmp SELECT 'API_APPLICATIONPROFILE_CREDIT_REPORTS', count(*), '' FROM API_APPLICATIONPROFILE_CREDIT_REPORTS
insert into #tmp SELECT 'API_ASSET', count(*), max(MODIFIED_AT) FROM API_ASSET
insert into #tmp SELECT 'API_CreditReport', count(*), max(MODIFIED_AT) FROM API_CreditReport
insert into #tmp SELECT 'API_DEALTEAM', count(*), max(MODIFIED_AT) FROM API_DEALTEAM
insert into #tmp SELECT 'API_Expense', count(*), max(MODIFIED_AT) FROM API_Expense
insert into #tmp SELECT 'API_HOI', count(*), max(MODIFIED_AT) FROM API_HOI
insert into #tmp SELECT 'API_HOI_TEST', count(*), max(MODIFIED_AT) FROM API_HOI_TEST
insert into #tmp SELECT 'API_INCOME', count(*), max(MODIFIED_AT) FROM API_INCOME
insert into #tmp SELECT 'API_OFFER', count(*), max(MODIFIED_AT) FROM API_OFFER
insert into #tmp SELECT 'api_overrides', count(*), max(MODIFIED_AT) FROM api_overrides
insert into #tmp SELECT 'API_PARTY', count(*), max(MODIFIED_AT) FROM API_PARTY
insert into #tmp SELECT 'API_PROFILE', count(*), max(MODIFIED_AT) FROM API_PROFILE
insert into #tmp SELECT 'API_Property', count(*), max(MODIFIED_AT) FROM API_Property
insert into #tmp SELECT 'API_TITLEREPORT', count(*), max(MODIFIED_AT) FROM API_TITLEREPORT
insert into #tmp SELECT 'API_TRADELINE', count(*), max(MODIFIED_AT) FROM API_TRADELINE
insert into #tmp SELECT 'API_USEOFPROCEEDS', count(*), max(MODIFIED_AT) FROM API_USEOFPROCEEDS
insert into #tmp SELECT 'API_USERINCOME', count(*), max(MODIFIED_AT) FROM API_USERINCOME
insert into #tmp SELECT 'API_VALUATION', count(*), max(MODIFIED_AT) FROM API_VALUATION
insert into #tmp SELECT 'AUTH_USER', count(*), '' FROM AUTH_USER
insert into #tmp SELECT 'DOC_DRAWN', count(*), '' FROM DOC_DRAWN
select * from #tmp
drop table if exists #tmp


--- FILE: DBSync\DBSync\SQL\Max_API_Table_Status_Snowflake.sql ---
SELECT 'API_ADDRESS' AS TABLENAME, count(*) AS ROW_COUNT, DATE(max(MODIFIED_AT)) AS MODIFIED_AT_DATE, TIME(max(MODIFIED_AT)) AS MODIFIED_AT_TIME  FROM RAW.fivetran_max_app_prod_public.API_ADDRESS
union all SELECT 'API_Application', count(*), DATE(max(MODIFIED_AT)) , TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_Application
union all SELECT 'API_APPLICATION_CREDIT_REPORTS', count(*), NULL, null FROM RAW.fivetran_max_app_prod_public.API_APPLICATION_CREDIT_REPORTS
union all SELECT 'API_APPLICATIONEXCEPTION', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONEXCEPTION
union all SELECT 'API_APPLICATIONPARTY', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONPARTY
union all SELECT 'API_APPLICATIONPROFILE', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONPROFILE
union all SELECT 'API_APPLICATIONPROFILE_CREDIT_REPORTS', count(*), NULL, null FROM RAW.fivetran_max_app_prod_public.API_APPLICATIONPROFILE_CREDIT_REPORTS
union all SELECT 'API_ASSET', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_ASSET
union all SELECT 'API_CreditReport', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_CreditReport
union all SELECT 'API_DEALTEAM', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_DEALTEAM
union all SELECT 'API_Expense', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_Expense WHERE IE_ISSUE_DATE >= '1/1/2019' or IE_ISSUE_DATE is null AND DELETED_AT IS NULL AND AMOUNT <> 0
union all SELECT 'API_HOI', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_HOI
union all SELECT 'API_INCOME', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_INCOME
union all SELECT 'API_OFFER', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_OFFER
union all SELECT 'api_overrides', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.api_overrides
union all SELECT 'API_PARTY', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_PARTY
union all SELECT 'API_PROFILE', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_PROFILE
union all SELECT 'API_Property', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_Property WHERE AQUIRED_ON >= '1/1/1902' or AQUIRED_ON is NULL
union all SELECT 'API_TITLEREPORT', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_TITLEREPORT
union all SELECT 'API_TRADELINE', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_TRADELINE
union all SELECT 'API_USEOFPROCEEDS', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_USEOFPROCEEDS
union all SELECT 'API_USERINCOME', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_USERINCOME
union all SELECT 'API_VALUATION', count(*), DATE(max(MODIFIED_AT)), TIME(max(MODIFIED_AT)) FROM RAW.fivetran_max_app_prod_public.API_VALUATION

union all SELECT 'AUTH_USER', count(*), NULL, null FROM RAW.fivetran_max_app_prod_public.AUTH_USER;


--- FILE: DBSync\DBSync\SQL\Outreach_Ops_Clear.sql ---
delete from OutreachOps


--- FILE: DBSync\DBSync\SQL\Outreach_Ops_Src.sql ---
SELECT OPPORTUNITY_ID, OPPORTUNITY_STAGE_ID, OPPORTUNITY_NAME, CREATED_AT, CREATED_AT_UTC, INVESTMENT_AMOUNT, ESTIMATED_SIGNING_DATE, PROBABILITY, TOUCHED_AT, UPDATED_AT, OWNER_ID  FROM UNLOCK_DBT_PROD.BRONZE_OUTREACH.OPPORTUNITIES


--- FILE: DBSync\DBSync\SQL\Outreach_OpUserMap_Clear.sql ---
delete from OutreachOppUserMap


--- FILE: DBSync\DBSync\SQL\Outreach_OpUserMap_Src.sql ---
SELECT OPPORTUNITY_ID, USER_ID  FROM UNLOCK_DBT_PROD.L01_SILVER_DIMS.OPPORTUNITY_ID_USER_MAP


--- FILE: DBSync\DBSync\SQL\Outreach_Prospects_Clear.sql ---
delete from OutreachPros


--- FILE: DBSync\DBSync\SQL\Outreach_Prospects_Src.sql ---
SELECT PROSPECT_ID, PERSONA_ID, ACCOUNT_ID, STAGE_ID, USER_ID, EMAIL, CREATED_AT, CREATED_AT_UTC, CREATED_AT_PT, TOUCHED_AT, ENGAGED_AT, SOURCE, NAME, OWNER_ID, LOSS_REASON, AD_NETWORK_ID, CAMPAIGN  FROM UNLOCK_DBT_PROD.BRONZE_OUTREACH.PROSPECTS


--- FILE: DBSync\DBSync\test.cs ---
namespace DBSync
{
    class test
    {
        public static string generateInsert(DataTable res, int id)
        {
            DataRow newestRecord = res.Rows[0];
            
            int newId = 1;

            
            string destTable = "API_SIDTEST";

            
            StringBuilder insertStatement = new StringBuilder();
            insertStatement.AppendFormat("INSERT INTO {0} (", destTable);

            
            for (int i = 0; i < res.Columns.Count; i++)
            {
                if (i > 0)
                {
                    insertStatement.Append(", ");
                }
                insertStatement.Append(res.Columns[i].ColumnName);
            }

            insertStatement.Append(") VALUES (");

            
            for (int i = 0; i < res.Columns.Count; i++)
            {
                if (i > 0)
                {
                    insertStatement.Append(", ");
                }

                if (res.Columns[i].ColumnName == "ID")
                {
                    insertStatement.Append(newId); 
                }
                else
                {
                    object value = newestRecord[res.Columns[i]];
                    if (value is string)
                    {
                        insertStatement.AppendFormat("'{0}'", value.ToString().Replace("'", "''")); 
                    }
                    else if (value is DateTime)
                    {
                        insertStatement.AppendFormat("'{0}'", ((DateTime)value).ToString("yyyy-MM-dd HH:mm:ss")); 
                    }
                    else
                    {
                        insertStatement.Append(value); 
                    }
                }
            }

            insertStatement.Append(");");

            return insertStatement.ToString();
        }
        public static void main(string[] args)
        {
            Query q = new Query("SELECT TOP 1 * FROM API_SIDTEST", "UAM_REPORTING");
            DataTable res = q.ExecuteTable();

            for (int i = 0; i < 10000000000; i++){
                Query q2 = new Query(generateInsert(res, i + 10000000), "UAM_REPORTING ");
                DataTable res2 = q.ExecuteTable();
            }
        }
  
    }
}


--- FILE: ZenSync\ZenSync\Program.cs ---
namespace ZenSync
{
    internal class Program
    {
        private const int UserBatchSize = 200;               
        private static readonly TimeSpan BatchPause = TimeSpan.FromMinutes(1); 
        private const string ConnectionName = "UAM_REPORTING";

        private static readonly HashSet<long> SkippedTicketIds = new HashSet<long>
        {
            34075, 35504, 36928, 36929, 37089, 37322, 37326, 37333, 37654, 37692,
            37827, 37910, 37975, 38039, 38343, 38416, 38518, 38545, 38670, 38749,
            38762, 38770, 38850, 38963, 39006, 39152, 39182, 39253, 39355, 39356,
            39435, 39468, 39503, 39604, 39635, 39846, 39964, 40002, 40102, 40112,
            40210, 40274, 40333, 40417, 40482, 40599, 40796, 40843, 40851, 40949,
            40979, 41285, 41296, 41347, 41408, 41442, 41782, 42165, 42261, 42265,
            42451, 42503, 42516, 42650, 42677, 42688, 42842, 42946, 42996, 43039,
            43084, 43092, 43135, 43142, 43185, 43198, 43246, 43293, 43399, 43459,
            43463, 43556, 43712, 43713, 44026, 44044, 44045, 44123, 44178, 44220,
            44240, 44352, 44646, 44659, 44670, 44859, 44870, 44918, 44983, 45007,
            45235, 45324, 45484, 45533, 45623, 45654, 45848, 45995, 46052, 46085,
            46211, 46280, 46484, 46636, 46721, 46838, 46864, 46865, 44909, 33034,
            38713, 44909, 38102, 38891
        };

        
        static async Task Main(string[] arg)
        {
            var cts = new CancellationTokenSource();
            var token = cts.Token;

            try
            {
                CommandLineArgs args = new CommandLineArgs(arg);

                string processName = args["processName"];
                if (string.IsNullOrWhiteSpace(processName))
                {
                    Console.WriteLine("Missing required argument: processName");
                    return;
                }

                string subdomain = "unlock957";
                string email = "badger@unlock.com"; 
                string apiToken = "XOWUkbDfQBJdlY6XLpJMTL5RK0jbXk2VaOEmz6gw";

                var zenAPI = new ZenAPI(subdomain, email, apiToken);

                bool fullReload = args.ContainsFlag("fullReload");
                string notificationRecipients = args.ArgIfAvailableNotNull<string>("notificationRecipients");
                Console.WriteLine(fullReload ? "Full reload enabled" : "Full reload disabled");

                switch (processName)
                {
                    case "load_users":
                        await LoadUsersAsync(fullReload, zenAPI, token);
                        break;

                    case "load_tickets":
                        await LoadTicketsAsync(fullReload, subdomain, email, apiToken, token);
                        break;

                    case "load_ticket":
                        await LoadSingleTicketAsync(args, subdomain, email, apiToken, token);
                        break;

                    case "load_settlement_requests":
                        await LoadSettlementRequestsAsync(fullReload, subdomain, email, apiToken, notificationRecipients, token);
                        break;

                    default:
                        Console.WriteLine("Process Name Not Valid");
                        break;
                }

                Console.WriteLine("Program Complete");
                await Task.Delay(4000, token); 
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine("Operation canceled.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Fatal error: " + ex.Message);
            }
        }

        private static async Task LoadUsersAsync(bool fullReload, ZenAPI zenAPI, CancellationToken token)
        {
            string query;
            if (fullReload)
            {
                query = "SELECT * FROM Applicants WHERE email IS NOT NULL AND full_name IS NOT NULL";
            }
            else
            {
                DateTime? lastRun = GetLastRunTime("load_users");
                if (lastRun == null)
                {
                    Console.WriteLine("No last run time found; performing full reload fallback.");
                    query = "SELECT * FROM Applicants WHERE email IS NOT NULL AND full_name IS NOT NULL";
                }
                else
                {
                    
                    query = "SELECT * FROM Applicants WHERE email IS NOT NULL AND full_name IS NOT NULL AND update_time > '" +
                            lastRun.Value.ToString("yyyy-MM-dd HH:mm:ss") + "'";
                }
            }

            Console.WriteLine(query);
            Query q = new Query(query, ConnectionName);
            DataTable tbl = q.ExecuteTable();

            if (tbl.Rows.Count == 0)
            {
                Console.WriteLine("No users to process.");
                UpdateLastRunTime("load_users");
                return;
            }

            var tasks = new List<Task>(capacity: UserBatchSize);
            int counter = 0;

            foreach (DataRow row in tbl.Rows)
            {
                token.ThrowIfCancellationRequested();

                int uid = SafeGetInt(row, "id");
                string userName = SafeGetString(row, "full_name"); 
                string userEmail = SafeGetString(row, "email");    
                int last4ssn = SafeGetInt(row, "ssn_last4", 0);    
                string phoneRaw = row["phone"]?.ToString();
                string phone = NormalizePhone(phoneRaw);

                if (string.IsNullOrWhiteSpace(userEmail) || string.IsNullOrWhiteSpace(userName))
                {
                    continue; 
                }

                tasks.Add(zenAPI.CreateUserAsync(userName, userEmail, last4ssn, phone, uid));
                counter++;

                if (counter % UserBatchSize == 0)
                {
                    Console.WriteLine($"Processing batch of {UserBatchSize} users, pausing for {BatchPause.TotalSeconds} seconds...");
                    await AwaitBatchAsync(tasks);
                    await Task.Delay(BatchPause, token);
                }
            }

            if (tasks.Count > 0)
            {
                Console.WriteLine($"Processing final batch of {tasks.Count} users...");
                await AwaitBatchAsync(tasks);
            }

            UpdateLastRunTime("load_users");
            Console.WriteLine("Task Completed!");
        }

        private static async Task LoadTicketsAsync(bool fullReload, string subdomain, string email, string apiToken, CancellationToken token)
        {
            DateTime? lastRun = GetLastRunTime("load_tickets");
            string date;

            if (fullReload)
            {
                date = "12/31/2024";
            }
            else if (lastRun.HasValue)
            {
                date = lastRun.Value.ToString("MM/dd/yyyy");
            }
            else
            {
                Console.WriteLine("No last run time; defaulting to 01/01/2000");
                date = "01/01/2000";
            }

            Console.WriteLine(date);
            ZenClient client = new ZenClient(ConnectionName, email, apiToken, "https:

            await client.SyncAllTickets(date, true);
            UpdateLastRunTime("load_tickets");
            Console.WriteLine("Task Completed!");
        }

        private static async Task LoadSingleTicketAsync(CommandLineArgs args, string subdomain, string email, string apiToken, CancellationToken token)
        {
            string ticketIdStr = args["ticket"];
            if (string.IsNullOrEmpty(ticketIdStr))
            {
                Console.WriteLine("Ticket ID is required for load_ticket process.");
                return;
            }

            if (!long.TryParse(ticketIdStr, out long ticketId))
            {
                Console.WriteLine("Invalid Ticket ID format.");
                return;
            }

            ZenClient client = new ZenClient(ConnectionName, email, apiToken, "https:
            await client.SyncTicket(ticketId);
            Console.WriteLine("Task Completed!");
        }

        private static async Task LoadSettlementRequestsAsync(bool fullReload, string subdomain, string email, string apiToken, string notificationRecipients, CancellationToken token)
        {
            DateTime? lastRun = GetLastRunTime("load_settlement_requests");
            string date;

            if (fullReload)
            {
                date = "12/31/2023";
            }
            else if (lastRun.HasValue)
            {
                date = lastRun.Value.ToString("MM/dd/yyyy");
            }
            else
            {
                Console.WriteLine("No last run time; defaulting to 01/01/2025");
                date = "01/01/2025";
            }

            Console.WriteLine("Settlement sync from: " + date);
            ZenClient client = new ZenClient(ConnectionName, email, apiToken, "https:

            await client.SyncSettlementRequests(date, SkippedTicketIds);
            UpdateLastRunTime("load_settlement_requests");
            Console.WriteLine("Settlement Request Sync Completed!");
        }

        private static DateTime? GetLastRunTime(string process)
        {
            try
            {
                string getLastRunQuery = "SELECT last_run_time FROM ZenSync_Runs WHERE process = '" + process + "'";
                Query glrq = new Query(getLastRunQuery, ConnectionName);
                DataTable glrqTbl = glrq.ExecuteTable();
                if (glrqTbl.Rows.Count == 0)
                    return null;

                object val = glrqTbl.Rows[0][0];
                if (val == null || val == DBNull.Value)
                    return null;

                DateTime dt;
                if (DateTime.TryParse(val.ToString(), out dt))
                    return dt;

                return null;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to retrieve last run time for " + process + ": " + ex.Message);
                return null;
            }
        }

        
        private static void UpdateLastRunTime(string process)
        {
            if (process != "load_users" && process != "load_tickets" && process != "load_settlement_requests")
                return; 

            try
            {
                string now = DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss");

                
                string existsSql = "SELECT COUNT(1) AS Cnt FROM ZenSync_Runs WHERE process = '" + process + "'";
                Query existsQ = new Query(existsSql, ConnectionName);
                DataTable existsTbl = existsQ.ExecuteTable();
                int count = 0;
                if (existsTbl.Rows.Count > 0)
                    int.TryParse(existsTbl.Rows[0][0].ToString(), out count);

                string sql;
                if (count > 0)
                {
                    sql = "UPDATE ZenSync_Runs SET last_run_time = '" + now + "' WHERE process = '" + process + "'";
                }
                else
                {
                    sql = "INSERT INTO ZenSync_Runs (process, last_run_time) VALUES ('" + process + "', '" + now + "')";
                }

                
                Query upsert = new Query(sql, ConnectionName);
                try
                {
                    
                    upsert.ExecuteTable(); 
                }
                catch
                {
                    
                }

                Console.WriteLine("Updated last_run_time for process: " + process + " at (UTC) " + now);
            }
            catch (Exception ex)
            {
                Console.WriteLine("Failed to update last_run_time for " + process + ": " + ex.Message);
            }
        }

        private static async Task AwaitBatchAsync(List<Task> tasks)
        {
            try
            {
                await Task.WhenAll(tasks);
            }
            catch (Exception ex)
            {
                Console.WriteLine("One or more user creation tasks failed: " + ex.Message);
            }
            finally
            {
                tasks.Clear();
            }
        }

        private static string NormalizePhone(string phoneRaw)
        {
            if (string.IsNullOrWhiteSpace(phoneRaw))
                return null;

            string digits = phoneRaw.Trim();
            if (!digits.StartsWith("+1"))
                digits = "+1" + digits;

            if (digits == "+1")
                return null;

            return digits;
        }

        private static string SafeGetString(DataRow row, string column)
        {
            if (!row.Table.Columns.Contains(column))
                return null;
            object val = row[column];
            return val == DBNull.Value ? null : val?.ToString();
        }

        private static int SafeGetInt(DataRow row, string column, int defaultValue = 0)
        {
            if (!row.Table.Columns.Contains(column))
                return defaultValue;
            object val = row[column];
            if (val == DBNull.Value || val == null)
                return defaultValue;
            int result;
            return int.TryParse(val.ToString(), out result) ? result : defaultValue;
        }
    }
}


--- FILE: ZenSync\ZenSync\Program1.cs ---
namespace ZenSync
{
    internal class Program
    {
        static void Main(string[] args)
        {
            ZenLib.Client.Test();
        }
    }
}


--- FILE: ZenSync\ZenSync\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("ZenSync")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("ZenSync")]
[assembly: AssemblyCopyright("Copyright ©  2022")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("4e28a084-00e0-4902-a8b3-1ec4af5a17e7")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: ZenSync\ZenSync\ZenAPI.cs ---
namespace ZenLib
{
    public class ZenAPI
    {
        private readonly string _subdomain;
        private readonly string _email;
        private readonly string _apiToken;
        private static Dictionary<string, int> emailLowestId = new Dictionary<string, int>();
        private static Dictionary<string, bool> processingEmails = new Dictionary<string, bool>();

        private readonly HttpClient _httpClient;
        private static readonly string logFilePath = "A:\\03 - Applications\\ZenSync\\zensync_failures.csv";

        public ZenAPI(string subdomain, string email, string apiToken)
        {
            _subdomain = subdomain;
            _email = email;
            _apiToken = apiToken;

            _httpClient = new HttpClient();
            _httpClient.BaseAddress = new Uri($"https:
            var authString = Convert.ToBase64String(Encoding.ASCII.GetBytes($"{_email}/token:{_apiToken}"));
            _httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Basic", authString);
        }


        
        public async Task CreateUserAsync(string userName, string userEmail, int last4ssn, string phone, int uid)
        {
            bool instance_running = false;
            if(!processingEmails.TryGetValue(userEmail, out instance_running))
            {
                instance_running = false;
            }
            int counter = 0;
            processingEmails[userEmail] = true;
            while (instance_running)
            {
                Random random = new Random();
                int sleepTimeInSeconds = random.Next(5, 10);
                await Task.Delay(sleepTimeInSeconds * 1000);
                instance_running = processingEmails[userEmail];
                counter++;
                if(counter > 5)
                {
                    break;
                }
            }
            processingEmails[userEmail] = true;
            using (var client = new HttpClient())
            {
                client.BaseAddress = new Uri($"https:

                
                var byteArray = Encoding.ASCII.GetBytes($"{_email}/token:{_apiToken}");
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", Convert.ToBase64String(byteArray));

                var user = new
                {
                    user = new
                    {
                        name = userName,
                        email = userEmail,
                        phone = phone,
                        role = "end-user",
                        user_fields = new
                        {
                            last_4_digits_of_ssn = last4ssn, 
                        }
                    }
                };

                var json = JsonConvert.SerializeObject(user);

                if(phone == null)
                {
                    var user_no_phone = new
                    {
                        user = new
                        {
                            name = userName,
                            email = userEmail,
                            role = "end-user",
                            user_fields = new
                            {
                                last_4_digits_of_ssn = last4ssn, 
                            }
                        }
                    };
                    json = JsonConvert.SerializeObject(user_no_phone);
                }

                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await client.PostAsync("users.json", content);

                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Created new user...");
                    emailLowestId[userEmail] = uid;
                    var responseData = await response.Content.ReadAsStringAsync();
                }
                else
                {
                    int prevId = 0;
                    bool prepend = false;

                    if(emailLowestId.TryGetValue(userEmail, out prevId))
                    {
                        if(prevId > uid)
                        {
                            prepend = true;
                            emailLowestId[userEmail] = uid;
                        }
                    }
                    else
                    {
                        emailLowestId[userEmail] = uid;
                    }

                    if((int) response.StatusCode == 422) {
                        
                        var searchResponse = await client.GetAsync($"users/search.json?query={userEmail}");
                        if (searchResponse.IsSuccessStatusCode)
                        {
                            var searchResult = await searchResponse.Content.ReadAsStringAsync();
                            dynamic searchResultJson = JsonConvert.DeserializeObject(searchResult);

                            if (searchResultJson.users.Count > 0)
                            {
                                var userId = searchResultJson.users[0].id;
                                var existingName = searchResultJson.users[0].name;

                                Console.WriteLine($"User found, updating user with ID: {userId}");
                                
                                string name = userName + ", " + existingName;

                                if (prevId == 0)
                                {
                                    name = userName;
                                }

                                var user2 = new
                                {
                                    user = new
                                    {
                                        name = name
                                    }
                                };

                                var updateJson = JsonConvert.SerializeObject(user2);


                                
                                if (!prepend && prevId != 0)
                                {
                                    var user3 = new
                                    {
                                        user = new
                                        {
                                            name = userName + ", " + existingName,
                                            phone = phone,
                                            user_fields = new
                                            {
                                                last_4_digits_of_ssn = last4ssn, 
                                            }
                                        }
                                    };
                                    updateJson = JsonConvert.SerializeObject(user3);
                                    if (phone == null)
                                    {
                                        var user3_no_phone = new
                                        {
                                            user = new
                                            {
                                                name = userName,
                                                email = userEmail,
                                                role = "end-user",
                                                user_fields = new
                                                {
                                                    last_4_digits_of_ssn = last4ssn, 
                                                }
                                            }
                                        };
                                        updateJson = JsonConvert.SerializeObject(user3_no_phone);
                                    }
                                }

                                var content2 = new StringContent(updateJson, Encoding.UTF8, "application/json");

                                
                                var updateResponse = await client.PutAsync($"users/{userId}.json", content2);
                                if (updateResponse.IsSuccessStatusCode)
                                {
                                    var updateData = await updateResponse.Content.ReadAsStringAsync();
                                    Console.WriteLine("User updated successfully: " + userId);
                                }
                                else
                                {
                                    Console.WriteLine("Failed to update user: " + updateResponse.StatusCode);
                                    var errorData = await updateResponse.Content.ReadAsStringAsync();
                                    Console.WriteLine("Error details: " + errorData);
                                    AppendErrorToCsv(uid, new Exception(errorData));
                                }
                            }
                            else
                            {
                                Console.WriteLine("No user found with that email.");
                            }
                        }
                        else
                        {
                            Console.WriteLine("Failed to search for the user: " + searchResponse.StatusCode);
                            var errorData = await searchResponse.Content.ReadAsStringAsync();
                            Console.WriteLine("Error details: " + errorData);
                            AppendErrorToCsv(uid, new Exception(errorData));
                        }

                    } else {
                        var errorData = await response.Content.ReadAsStringAsync();
                        Console.WriteLine("Error details: " + errorData);
                        AppendErrorToCsv(uid, new Exception(errorData));
                    }

                }
            }
            processingEmails[userEmail] = false;
        }

        public static object GetCustomFieldValue(JToken customFieldsToken, long fieldId)
        {
            JArray customFields = customFieldsToken as JArray;
            foreach (var field in customFields)
            {
                if ((long)field["id"] == fieldId)
                {
                    return field["value"];
                }
            }
            return null; 
        }


        
        public async Task TransferAssetIdToTicketsAsync(long? startingUserId = null)
        {
            
            Console.WriteLine("Fetching users...");
            var users = await FetchAllUsersAsync(startingUserId);

            foreach (var user in users)
            {
                try {
                    
                    var assetId = GetUserAssetId(user);

                    if (!string.IsNullOrEmpty(assetId))
                    {
                        Console.WriteLine($"Processing user: {user["id"]} with asset_id: {assetId}");

                        
                        var tickets = await FetchUserTicketsAsync((long)user["id"]);
                        if(tickets.Count == 0)
                        {
                            Console.WriteLine("No tickets to process " + tickets.Count);
                        }

                        
                        foreach (var ticket in tickets)
                        {
                            await UpdateTicketWithAssetIdAsync((long)ticket["id"], assetId);
                        }
                        if (tickets.Count != 0)
                        {
                            Console.WriteLine("Successfully Added User's Tickets");
                        }
                    }
                    else
                    {
                        Console.WriteLine($"User: {user["id"]} has no asset_id associated");
                        
                        var tickets = await FetchUserTicketsAsync((long)user["id"]);
                        if (tickets.Count == 0)
                        {
                            Console.WriteLine("No tickets to process " + tickets.Count);
                        }
                        
                        foreach (var ticket in tickets)
                        {
                            string asset_id = GetCustomFieldValue(ticket["custom_fields"], 5578383498523)?.ToString();

                            await UpdateTicketWithAssetIdAsync((long)ticket["id"], asset_id);
                        }
                        if (tickets.Count != 0)
                        {
                            Console.WriteLine("Successfully Added User's Tickets");
                        }
                    }
                } 
                catch (Exception ex)
                {
                    Console.WriteLine("Appending to Error CSV");
                    AppendErrorToCsv((long)user["id"], ex);
                }
                System.Threading.Thread.Sleep(1000);
            }
        }
        private void AppendErrorToCsv(long userId, Exception ex)
        {
            
            string[] errorDetails = {
                $"\"{DateTime.Now:yyyy-MM-dd HH:mm:ss}\"",
                $"\"{userId}\"",
                $"\"{ex.Message.Replace("\"", "\"\"")}\"",  
                $"\"{ex.StackTrace?.Replace("\n", " ").Replace("\r", " ").Replace("\"", "\"\"")}\"" 
            };
            StreamWriter writer = null;
            
            try
            {
                
                writer = new StreamWriter(logFilePath, true);

                
                if (new FileInfo(logFilePath).Length == 0)
                {
                    writer.WriteLine("Timestamp,UserID,ErrorMessage,StackTrace");
                }

                
                writer.WriteLine(string.Join(",", errorDetails));
                Console.WriteLine("Error logged to CSV file.");
            }
            catch (Exception fileEx)
            {
                Console.WriteLine($"Failed to write to log file: {fileEx.Message}");
            }
            finally
            {
                
                if (writer != null)
                {
                    writer.Close();
                }
            }
        }
        private string GetUserAssetId(JObject user)
        {
            
            var userFields = (JObject)user["user_fields"];
            return userFields?["asset_id"]?.ToString();
        }

        private async Task<JObject> FetchUserByIdAsync(long userId)
        {
            
            var response = await _httpClient.GetAsync($"users/{userId}.json");
            var content = await response.Content.ReadAsStringAsync();

            
            if (!response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Error fetching user with ID {userId}: " + content);
                return null;  
            }

            
            var json = JObject.Parse(content);
            var user = (JObject)json["user"];  

            return user;
        }


        private async Task<List<JObject>> FetchAllUsersAsync(long? startingUserId = null)
        {
            var usersList = new List<JObject>();
            int page = 1;
            bool moreUsers = true;

            while (moreUsers)
            {
                var url = $"users.json?page={page}&per_page=100";
                if (startingUserId.HasValue)
                {
                    url += $"&starting_after={startingUserId.Value}";
                }

                var response = await _httpClient.GetAsync(url);
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Error fetching users: " + content);
                    break;
                }

                var json = JObject.Parse(content);
                var users = (JArray)json["users"];
                if (users.Count == 0)
                {
                    moreUsers = false;
                }
                else
                {
                    usersList.AddRange(users.ToObject<List<JObject>>());
                    page++;
                }
            }

            return usersList;
        }

        private async Task<List<JObject>> FetchUserTicketsAsync(long userId)
        {
            var ticketsList = new List<JObject>();
            int page = 1;
            bool moreTickets = true;

            while (moreTickets)
            {
                
                var response = await _httpClient.GetAsync($"search.json?query=type:ticket+requester_id:{userId}+status<closed&page={page}");
                var content = await response.Content.ReadAsStringAsync();

                if (!response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Error fetching tickets for user {userId}: " + content);
                    break;
                }

                var json = JObject.Parse(content);
                var tickets = (JArray)json["results"];
                if (tickets.Count == 0)
                {
                    moreTickets = false;
                }
                else
                {
                    ticketsList.AddRange(tickets.ToObject<List<JObject>>());
                    page++;
                }
            }

            return ticketsList;
        }

        public async Task UpdateTicketWithAssetIdAsync(long ticketId, string assetId)
        {
            string query_assets = "SELECT address_simple, city, state, zip, investment_payment, starting_home_value, exchange_rate, cost_limit, effective_date FROM Assets WHERE id = '"+assetId+"'";
            Query q_assets = new Query(query_assets, "UAM_REPORTING");
            DataTable assets_tbl = q_assets.ExecuteTable();
            DataRow asset_row = assets_tbl.Rows[0];

            var address = asset_row[0];
            var city = asset_row[1];
            var state = asset_row[2];
            var zip_code = Int32.Parse((string) asset_row[3]);
            var investment_payment = "$" + asset_row[4];
            var starting_home_val = "$" + asset_row[5].ToString();
            var exchange_rate = double.Parse(asset_row[6].ToString());
            var cost_limit = double.Parse(asset_row[7].ToString());
            string effective_date = DateTime.Parse(asset_row[8].ToString()).ToString("yyyy-MM-dd");

            string query_vassets = "SELECT investment_pct, unlock_pct FROM vAssets WHERE asset_id = '" + assetId+"'";
            Query q_vassets = new Query(query_vassets, "UAM_REPORTING");
            DataTable vassets_tbl = q_vassets.ExecuteTable();
            DataRow vasset_row = vassets_tbl.Rows[0];

            var homeowner_docs = "https:
            var investment_pct = double.Parse(vasset_row[0].ToString());
            var unlock_percentage = double.Parse(vasset_row[1].ToString());

            var ticketUpdate = new
            {
                ticket = new
                {
                    custom_fields = new List<object>
                    {
                        new {
                            id = 5578383498523, 
                            value = assetId
                        },
                        new {
                            id = 29886444203931,
                            value = address
                        }, 
                        new {
                            id = 29886481166747,
                            value = city
                        }, 
                        new {
                            id = 29886515721371,
                            value = state
                        }, 
                        new { 
                            id = 29886676716699,
                            value = zip_code 
                        },
                        new {
                            id = 29886518754971,
                            value = homeowner_docs
                        },
                        new {
                            id = 29886539567003,
                            value = effective_date
                        }, 
                        new {
                            id = 29886528417947,
                            value = starting_home_val
                        },
                        new {
                            id = 29886573529499,
                            value = investment_payment
                        },
                        new {
                            id = 29886580499739,
                            value = investment_pct
                        },
                        new {
                            id = 29886597300123,
                            value = exchange_rate
                        },
                        new {
                            id = 29886550428955,
                            value = unlock_percentage
                        },
                        new {
                            id = 29886552012187,
                            value = cost_limit
                        }
                    }
                }
            };

            var json = JsonConvert.SerializeObject(ticketUpdate);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PutAsync($"tickets/{ticketId}.json", content);

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine($"Successfully updated ticket: {ticketId} with asset_id: {assetId}");
            }
            else
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                Console.WriteLine($"Failed to update ticket: {ticketId} - {errorContent} ... Sleeping now");
                System.Threading.Thread.Sleep(60000);
                response = await _httpClient.PutAsync($"tickets/{ticketId}.json", content);
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Successfully updated ticket: {ticketId} with asset_id: {assetId}");
                }
                else
                {
                    Console.WriteLine($"FATAL: Failed to update ticket: {ticketId} - {errorContent}");
                }
            }
        }
    }

}


--- FILE: MailSync\MailSync\Program.cs ---
namespace MailSync
{
    internal class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string display_name = args["displayname"];
            string server = args["server"];
            bool write = args.ContainsFlag("write");

            MailLib.MailReader m = new MailLib.MailReader("Support");
            m.SetSyncServer(server);
            m.Sync(write);
        }
    }
}


--- FILE: MailSync\MailSync\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("MailSync")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("MailSync")]
[assembly: AssemblyCopyright("Copyright ©  2022")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("f050a865-09cf-46b2-9f30-72207145b6eb")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: BigDoughLoader\BigDoughLoader\Program.cs ---
namespace BigDoughLoader
{
    class Program
    {
        static void Main(string[] arg)
        {

            
            {
                CommandLineArgs args = new CommandLineArgs(arg);
                string export = args["export"];
                string server = args["server"];
                bool archive = args.ContainsFlag("archive");
                bool do_scrape = args.ContainsFlag("doscrape");
                bool load = args.ContainsFlag("load");
                string bduser = null;
                string bdpass = null;
                if (args.ContainsFlag("bduser"))
                    bduser = args["bduser"];
                if (args.ContainsFlag("bdpass"))
                    bdpass = args["bdpass"];
                string email = null;
                if (args.ContainsFlag("email"))
                    email = args["email"];
                int loaded = 0;
                string sql = null;
                if (args.ContainsFlag("sql")) 
                    sql = args["sql"];
                int? how_many = null;
                if (args.ContainsFlag("howmany"))
                    how_many = System.Convert.ToInt32(args["howmany"]);

                string to = "dfoster@rwbaird.com";
                if (args.ContainsFlag("to"))
                    to = args["to"];

                string smtp_server = args["smtp_server"];
                bool do_scrape_portfolios = args.ContainsFlag("do_scrape_portfolios");

                IWriter writer = Console.WriteLine;
                bool success = false;
                Scraper s = null;
                if (do_scrape)
                {
                    s = new Scraper(bduser, bdpass, server, export);
                    var rnd = new Random(DateTime.Now.Millisecond);
                    how_many = rnd.Next(475, 499);
                    s.LoadUpcomingBWICCusips(how_many.Value,sql);
                    if (s.total_cusips != 0)
                    {
                        s.PopulateLoadId();
                        s.Scrape();
                        success = true;
                        
                    }

                    s.Exit();
                }

                if (do_scrape_portfolios)
                {


                    s = new Scraper(bduser, bdpass, server, export);
                    s.LoadUpcomingAccounts(how_many.Value, sql);



                    if (s.total_cusips != 0)
                    {
                        
                        s.ScrapeAccounts();
                        success = true;

                    }

                    s.Exit();
                }

                if (load)
                {
                    loaded = BigDoughLib.Loader.HandleLoad(server, export, archive, writer);
                    success = true;
                }

                if(null != s && success)
                {
                    if(null != s.load_id)
                        s.RecordLoadAttempt();
                }

                if (loaded > 0 && !String.IsNullOrEmpty(email))
                {
                    string from = "BDLoader@rwbaird.com";
                    UtilsLib.Mail m = new Mail(from, smtp_server, null, null);
                    m.SendSMTPMail(to, null, null, "BD Load: " + loaded, null, null, false, true,from);
                    
                }
            }
            
            {
                
            }
        }
    }
}


--- FILE: BigDoughLoader\BigDoughLoader\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("BigDoughLoader")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("BigDoughLoader")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2017")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("dcc3d267-6a78-4501-959a-7c5adb2f6fec")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: BankLoader\BankLoader\Program.cs ---
namespace BankLoader
{
    class Program
    {
        static async Task Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string user = args["user"];
            string pass = args["pass"];
            string mail_profile = args["mailprofile"];
            string notify = args["notify"];
            string server = args["server"];
            
            string post_cmd = args["postcmd"];
            bool update_max = args.ContainsFlag("updatemax");

            BankLib.Loader l = new Loader(user, pass);
            l.StartLoad(server, mail_profile, notify, post_cmd);

            Mail m = new Mail(mail_profile);
            SClient sc = new SClient();

            List<string> asset_ids = BadgerLib.Closing.GetRequiredMaxFundingUpdates(server);

            if (update_max && asset_ids.Count > 0)
            {
                bool result;
                foreach (string asset_id in asset_ids)
                {
                    result = await MaxDocVaultLib.MaxDocVault.UpdateSubstageToPendingRecording(asset_id);
                    string name_simple = BadgerLib.Assets.GetNameSimple(server, asset_id);

                    if (result == true)
                    {
                        sc.SendMessage(SClient.RECIPIENT.post_closing, $"{asset_id} - {name_simple}: Deal Funded!", true);
                        sc.SendMessage(SClient.RECIPIENT.badger_growls, $"{asset_id} - {name_simple}: Deal Funded!", true);
                    }
                    else
                        m.SendSMTPMail(notify, null, null, string.Concat(asset_id, " - Max SubStage not updated to Pending Recording"), null, null, true, true, null, MailPriority.Normal);
                }
            }

            
            

            
            
            
            

            

            

            
        }
    }
}


--- FILE: BankLoader\BankLoader\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("BankLoader")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("BankLoader")]
[assembly: AssemblyCopyright("Copyright ©  2021")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("c263d443-3d04-424c-8530-cf17768479ec")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: DBLoader\DBLoader\Program.cs ---
[assembly: log4net.Config.XmlConfigurator(ConfigFile = "log4net.config", Watch = true)]

namespace DBLoader
{
    class Program
    {
        
        static Program()
        {
            System.Net.ServicePointManager.SecurityProtocol = 
                SecurityProtocolType.Tls12 | SecurityProtocolType.Tls13;
        }

        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);

            string to = args.ContainsFlag("to") ? args["to"] : null;
            string errormails = args.ContainsFlag("errormails") ? args["errormails"] : null;
            string from = args.ContainsFlag("from") ? args["from"] : null;
            string cc = "";
            string loadtype = args["loadtype"];
            bool dbload = args.ContainsFlag("dbload");

            
            string env = args.ContainsFlag("env") ? args["env"] : "PROD";
            Constants.SetEnvironment(Constants.GetEnvironment(env));

            Dictionary<string, object> parms = new Dictionary<string, object>();

            if (null == errormails)
                errormails = to + ((null == cc) ? "" : (";" + cc));
            try
            {
                string folder = args.ContainsFlag("folder") ? args["folder"] : null;
                string post_cmd = args.ContainsFlag("postcmd") ? args["postcmd"] : null;
                bool archive = args.ContainsFlag("archive");
                string server = args["server"];
                
                Mail.MailServerConfig mail_profile = new Mail.MailServerConfig
                {
                    server = args.ArgIfAvailableNotNull<string>("smtp_server"),
                    user = args.ArgIfAvailableNotNull<string>("smtp_user"),
                    pass = args.ArgIfAvailableNotNull<string>("smtp_pass"),
                    port = args.ArgIfAvailableNotNull<int>("smtp_port", 25)
                };

                if (args.ContainsFlag("mailprofile"))
                    mail_profile = UtilsLib.Mail.MailProfiles.GetProfiles()[args["mailprofile"]];
                
                bool mail = args.ContainsFlag("mail");

                if (args.ContainsFlag("PARAMS"))
                    parms = args.GetDictionary<object>(args["PARAMS"]);

                cc = args.ContainsFlag("cc") ? args["cc"] : null;                
                bool file_found = args.ContainsFlag("found");
                bool no_mail = args.ContainsFlag("nomail");
                bool ignoreext = args.ContainsFlag("ignoreext");
                string subject_raw = args.ContainsFlag("subject") ? args["subject"] : null;
                bool zip = args.ContainsFlag("ziparchive");
                bool loaderAlreadyRan = false;
                if (no_mail)
                    mail = false;

                List<Task> all_tasks = new List<Task>();
                List<string> files = new List<string>();
                if(!dbload)
                {
                    files = Directory.GetFiles(folder).OrderBy(f => new FileInfo(f).Length).ToList();
                }
                else
                {
                    files.Add(null);
                }
                
                foreach (string file in files)
                {
                     if (loaderAlreadyRan)
                        return;
                    if (null != file) {

                        if (file.Contains("~$") || file.Contains("tmp")) {
                            try {
                                File.Delete(file);
                            }
                            catch {
                                Console.WriteLine("Tried To Delete & Failed: " + file);
                            }
                            continue;
                        }
                    }

                    DBOutputHelper items = null;                       
                    Nullable<int> process_id = null;

                    try
                    {
                        if(null != file)
                            Console.WriteLine("Found File: " + file);

                        if (mail && file_found && !no_mail && null != file)
                        {
                            Mail m = new Mail(mail_profile);
                            m.SendSMTPMail(to, cc, null, "Export Found: " + file, null, null, false, true, from);
                        }

                        IDBLoader loader = null;
                        switch (loadtype)
                        {
                            case "clearedgewirereport": 
                                loader = new ClearEdgeWireReportHelper(server); break;
                            case "clearedge":
                                loader = new ClearEdgeHelper(server); break;
                            case "WSFS":        
                                loader = new WSFSHelper(server); break;
                            case "wsfs_trust":
                                loader = new WSFSParserTrust(server); break;
                            case "wsfsactivity":  
                                loader = new WSFSActivityHelper(server); break;
                            case "lienalert":   
                                loader = new LienAlertHelper(server); break;
                            case "usbank":      
                                loader = new USBankHelper(server); break;
                            case "snowflake":   
                                loader = new SnowflakeHelper(server); break;
                            case "jpm":
                                loader = new JPMHelper(server, false);
                                loaderAlreadyRan = true;
                                break;
                            case "maxwell":     
                                loader = new MaxwellHelper(server); break;
                            case "crs":
                                loader = new CreditLib.CRSRunner(server); break;
                            case "tcb":
                                loader = new TCBHelper(server);
                                loaderAlreadyRan = true;
                                break;
                            case "fa_lienrelease":
                                loader = new LienReleaseParser(server);
                                loaderAlreadyRan = true;
                                break;
                            case "fa_assignment_report_processing":
                                loader = new AssignmentReporter(server);
                                loaderAlreadyRan = true;
                                break;
                            case "fa_assignment_submit":
                                loader = new AssignmentSender(server);
                                loaderAlreadyRan = true;
                                break;
                            case "fa_reconveyance":
                                loader = new ReconveyanceParser(server);
                                loaderAlreadyRan = true;
                                break;

                            case "tcbcheckrequest":
                            {
                                
                                
                                
                                
                                
                                string ckInputFolder  = args.ContainsFlag("folder")
                                    ? args["folder"] : null;
                                string ckOutputFolder = args.ContainsFlag("outputfolder")
                                    ? args["outputfolder"] : null;
                                string ckArchiveFolder = args.ContainsFlag("archivefolder")
                                    ? args["archivefolder"]
                                    : @"A:\01 - Surveillance\TCB\CheckRequestsArchive";
                                bool ckDryRun = args.ContainsFlag("dryrun");
                                int? ckMaxFiles = args.ContainsFlag("maxfiles")
                                    ? (int?)int.Parse(args["maxfiles"])
                                    : null;

                                var ckConfig = new TCBCheckRequestConfig
                                {
                                    Server        = server,
                                    InputFolder   = ckInputFolder,
                                    OutputFolder  = ckOutputFolder,
                                    ArchiveFolder = ckArchiveFolder,
                                    DryRun        = ckDryRun,
                                    MaxFiles      = ckMaxFiles
                                };

                                var ckProcessor = new TCBCheckRequestProcessor(ckConfig);
                                TCBCheckRequestProcessResult ckResult =
                                    ckProcessor.ProcessNewRequests();

                                string ckEmailBody = null;
                                List<string> ckAttachments = null;
                                if (ckResult.Files != null && ckResult.Files.Count > 0)
                                {
                                    var sb = new System.Text.StringBuilder();
                                    sb.AppendLine("<html><body>");
                                    sb.AppendLine($"<p>TCBCheckRequest load completed. " +
                                        $"scanned={ckResult.TotalScanned}, " +
                                        $"processed={ckResult.TotalProcessed}, " +
                                        $"skipped={ckResult.TotalSkipped}, " +
                                        $"failed={ckResult.TotalFailed}, " +
                                        $"csvRows={ckResult.TotalCsvRows}</p>");
                                    sb.AppendLine("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>");
                                    sb.AppendLine("<tr style='background-color: #f0f0f0;'><th>File</th><th>Status</th><th>Load ID</th><th>Rows</th><th>CSV / Error</th></tr>");
                                    ckAttachments = new List<string>();
                                    foreach (var f in ckResult.Files)
                                    {
                                        string detail = f.Status == FileStatus.Failed
                                            ? WebUtility.HtmlEncode(f.Error ?? "")
                                            : (f.CsvPath ?? "");
                                        sb.AppendLine($"<tr><td>{WebUtility.HtmlEncode(f.FileName ?? "")}</td>" +
                                                      $"<td>{f.Status}</td>" +
                                                      $"<td>{(f.LoadId.HasValue ? f.LoadId.Value.ToString() : "")}</td>" +
                                                      $"<td>{f.CsvRowCount}</td>" +
                                                      $"<td>{detail}</td></tr>");
                                        if (f.Status == FileStatus.Processed
                                            && !string.IsNullOrEmpty(f.CsvPath)
                                            && File.Exists(f.CsvPath))
                                        {
                                            ckAttachments.Add(f.CsvPath);
                                        }
                                    }
                                    sb.AppendLine("</table>");
                                    sb.AppendLine("</body></html>");
                                    ckEmailBody = sb.ToString();
                                    if (ckAttachments.Count == 0) ckAttachments = null;
                                }

                                items = new DBOutputHelper
                                {
                                    rows = ckResult.TotalCsvRows,
                                    email_subj_override = ckResult.TotalProcessed > 0
                                        ? $"TCBCheckRequest load complete — {ckResult.TotalProcessed} file(s), {ckResult.TotalCsvRows} check(s)"
                                        : (ckResult.TotalFailed > 0
                                            ? $"TCBCheckRequest load FAILED for {ckResult.TotalFailed} file(s)"
                                            : ""),
                                    email_body_override = ckEmailBody,
                                    email_attachments   = ckAttachments
                                };
                                loaderAlreadyRan = true;
                                break;
                            }

                            case "mtsettlementtrans":
                            {
                                
                                
                                
                                string outputFolder = args.ContainsFlag("folder") ? args["folder"] : null;
                                bool dryRun = args.ContainsFlag("dryrun");
                                int? batchSize = args.ContainsFlag("batchsize")
                                    ? (int?)int.Parse(args["batchsize"])
                                    : null;

                                var config = new MTSettlementTransConfig
                                {
                                    Server           = server,
                                    OutputRootFolder = outputFolder,
                                    DryRun           = dryRun,
                                    BatchSize        = batchSize
                                };

                                var processor = new MTSettlementTransProcessor(config);
                                ProcessResult result = processor.ProcessNewSettlements();

                                
                                string emailBody = null;
                                List<string> attachments = null;
                                if (result.Rows != null && result.Rows.Count > 0)
                                {
                                    var sb = new System.Text.StringBuilder();
                                    sb.AppendLine("<html><body>");
                                    sb.AppendLine("<p>MTSettlementTrans load completed successfully.</p>");
                                    sb.AppendLine("<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>");
                                    sb.AppendLine("<tr style='background-color: #f0f0f0;'><th>Asset ID</th><th>Account</th><th>Description</th><th>Amount</th></tr>");
                                    foreach (var row in result.Rows)
                                    {
                                        sb.AppendLine($"<tr><td>{row.AssetId}</td><td>{row.AccountName}</td><td>{row.Description}</td><td>{row.Amount:C2}</td></tr>");
                                    }
                                    sb.AppendLine("</table>");
                                    sb.AppendLine("</body></html>");
                                    emailBody = sb.ToString();

                                    
                                    if (!string.IsNullOrEmpty(result.CsvPath) && File.Exists(result.CsvPath))
                                    {
                                        attachments = new List<string> { result.CsvPath };
                                    }
                                }

                                items = new DBOutputHelper
                                {
                                    rows = result.CsvRowCount,
                                    email_subj_override = result.CsvRowCount > 0
                                        ? $"MTSettlementTrans load complete — {result.TotalProcessed} settlements, {result.CsvRowCount} rows, load_id={result.LoadId}"
                                        : "",
                                    email_body_override = emailBody,
                                    email_attachments = attachments
                                };
                                loaderAlreadyRan = true;
                                break;
                            }
                        }

                        if (null != loader)
                        {
                            loader.WriteToDatabase(true);
                            loader.SetWriter(Console.WriteLine);
                            process_id = loader.StartExcel();
                            loader.LoadFile(file);
                            loader.PassParms(parms);
                            items = loader.ParseAndLoad();
                            loader.FinishUp();
                        }

                        if (archive)
                        {
                            string archive_path = Path.GetDirectoryName(file) + @"\Archive";
                            UtilsLib.FileLib.WaitForFile(file, 30 * 1000);
                            UtilsLib.FileLib.ArchiveFile(archive_path, file, "M.d.yy - H.mmss", true, loader.asOf, ignoreext,zip);
                        }

                        if (mail)
                        {
                            bool isRowsNullOrZero = items?.rows == null || items?.rows == 0;
                            bool isEmailSubjOverrideNullOrZero = items?.email_subj_override == null || items?.email_subj_override.Length == 0;
                            if (isRowsNullOrZero && isEmailSubjOverrideNullOrZero)
                                continue;

                            Dictionary<string, object> more = new Dictionary<string, object>();
                            parms.ToList().ForEach(n => more.Add(n.Key, n.Value));
                            more.Add("@total", items?.rows.ToString());
                            if(loader != null && loader.asOf != null)
                                more.Add("@asOf", loader.asOf.Value.ToString("MM/dd/yyyy"));
                            
                            
                            string subject = !string.IsNullOrEmpty(items?.email_subj_override)
                                ? items.email_subj_override
                                : UtilsLib.Clean.CommonVariables(subject_raw, "/", more);
                            Mail m = new Mail(mail_profile);
                            if (!string.IsNullOrEmpty(items?.email_to_override))
                                to = items?.email_to_override;
                            bool isHtml = !string.IsNullOrEmpty(items?.email_body_override);
                            m.SendSMTPMail(to, cc, null, subject, items?.email_body_override, items?.email_attachments, isHtml, true, from);
                        }

                        if (!String.IsNullOrEmpty(post_cmd))
                        {
                            Process p = new Process();
                            string working_directory = Path.GetDirectoryName(post_cmd);
                            p.StartInfo.WorkingDirectory = working_directory;
                            p.StartInfo.FileName = post_cmd;
                            p.Start();
                        }

                    }
                    catch (Exception n)
                    {
                        if (null != process_id)
                            UtilsLib.ProcessHelper.KillProcess(process_id.Value);
                        
                        UtilsLib.Error.SendError(errormails, CommonInterfaces.Constants.ERROR_EMAIL, "DB Loader", n, args.ArgDump, true);
                    }
                }                
            }
            catch(Exception n)
            {
                UtilsLib.Error.SendError(to, from, "DB Loader",n, null, true);
            }            
        }

        public class ParseHelper
        {
            public string file { get; set; }
            public bool mail { get; set; }
            public bool file_found { get; set; }
            public bool no_mail { get; set; }
            public string from { get; set; }
            public string smtp_server { get; set; }
            public string to { get; set; }
            public string cc { get; set; }
            public string subject { get; set; }
            public string server { get; set; }
            public string loadtype { get; set; }
            public bool archive { get; set; }
            public bool ignoreext { get; set; }
            public bool async { get; set; }
            public bool zip { get; set; }                        
        }
    }
}


--- FILE: DBLoader\DBLoader\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("DBLoader")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("DBLoader")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2017")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("9feee126-5557-4272-8c5d-c176172a01f3")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: IPREOLoader\IPREOLoader\Program.cs ---
namespace IPREOLoader
{
    class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string path = args["path"];
            string server = args["server"];
            
            string sql = Database.TableClass.Generate(@"C:\Visual Studio Projects\IPREOLib\bin\Debug\IPREOLib.dll");
            IEnumerable<string> files = Directory.GetFiles(path, "rwbord*.xml");
            ETA eta = new ETA(files.Count(), Console.WriteLine);
            foreach (string filename in files)
            {
                XmlSerializer serializer = new XmlSerializer(typeof(IPREOLib.Xml2CSharp.Ideal_audit));

                
                FileStream fs = new FileStream(filename, FileMode.Open);
                XmlReader reader = XmlReader.Create(fs);

                
                Ideal_audit i;
                
                eta.IncrementAndReport();
                
                i = (Ideal_audit)serializer.Deserialize(reader);
                Write.RecordOrder(server,i.Audit_orders.IPREOOrder);
                fs.Close();
            }
        }

      
    }
}


--- FILE: IPREOLoader\IPREOLoader\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("IPREOLoader")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("IPREOLoader")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2018")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("377c20f0-69c3-42a8-84c2-296e8da09063")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: BatSignal\BatSignal\Program.cs ---
namespace Bat_Signal_Cmd
{
    class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string to = args["to"];
            
           
                
            string signalr = args["signalr"];
            BatSignalLib.Server s = new Server();
            
            
            BatSignalLib.Server.StartService(signalr);
            
            Console.ReadLine();
            
            
            
            
            
        }
    }



}


--- FILE: BatSignal\BatSignal\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("Bat Signal Cmd")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("Bat Signal Cmd")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2018")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("1182074b-a57a-4ce1-aad2-ec5b44de5a2e")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: BatSignalLib\AlertHelper.cs ---
namespace BatSignalLib
{
    public class AlertHelper
    {
        public Nullable<int> tab_id { get; internal set; }
        public Nullable<int> respective_id { get; internal set; }
        public string caption { get; internal set; }
        public string message { get; internal set; }
        public string hot_text { get; internal set; }
        public List<string> groups { get; internal set; }
        public string username {  get; set; }
        public bool hide_if_me {  get; set;}

        public AlertHelper(int? tab_id, int? respective_id, string caption, string message, string hot_text,IEnumerable<string> groups,string from_username,bool hide_if_me)
        {
            this.tab_id = tab_id;
            this.respective_id = respective_id;
            this.caption = caption;
            this.message = message;
            this.hot_text = hot_text;
            this.groups = groups?.ToList().ConvertAll(d => d.ToUpper());
            this.username = from_username;
            this.hide_if_me = hide_if_me;
        }
    }

    public class AssetUpdateHelperSignal
    {
        public string server;
        public List<string> assets;
        public bool force;
        public bool include_bulk;
        public List<string> db_fields;
        public bool do_not_update_if_in_db;
        public string group;
    }




}


--- FILE: BatSignalLib\Classes.cs ---
namespace BatSignalLib
{
    public class Classes
    {
        public class RestartHelper
        {
            public string group;
            public int seconds;
        }


        public class Users
        {
            public string user_id;
            public string computername;
            public List<string> groups;
            public string connection_id;
            public DateTime connection_time;
            public override string ToString()
            {
                return user_id;
            }
        }

    }
}


--- FILE: BatSignalLib\ConnectionManager.cs ---
namespace BatSignalLib
{
    public class ConnectionManager
    {
        public class UserConnection
        {
            public string connection_id;
            public string user_id;
            public DateTime connect_time;
        }


        
        public static Dictionary<string, UserConnection> GetInstance()
        {
            if(null == _connections)
                _connections = new Dictionary<string, UserConnection>();
            return _connections;
        }

        public static Dictionary<string, UserConnection> _connections;

    }
}


--- FILE: BatSignalLib\ConnectionTracker.cs ---
namespace BatSignalLib
{
    public class ConnectionTracker
    {
      
    }

    public class CUser
    {
        public string username;
        public List<string> comptuers = new List<string>();
        public string program;
    }
}


--- FILE: BatSignalLib\Extensions.cs ---
namespace BatSignalLib
{
    public static class Extensions
    {
        public static string CurrentUserName(this Microsoft.AspNet.SignalR.Hubs.HubCallerContext cow)
        {
            try
            {
                string user = cow.User.Identity.Name.Substring(cow.User.Identity.Name.IndexOf(@"\") + 1).ToUpper();
                return user;
            }
            catch (Exception n)
            {

            }
            
            return "<UKNOWN>";
        }
    }
}


--- FILE: BatSignalLib\Main.cs ---
namespace BatSignalLib
{
    public class SignalRClient
    {
        private IHubProxy HubProxy { get; set; }
        private HubConnection Connection { get; set; }
        string _full_server;

        public void Init(string full_server)
        {
            _full_server = full_server;
        }

        private List<string> log = new List<string>();

        public void AddLog(string message)
        {
            string msg = $"[{DateTime.Now}] - {message}";
            log.Add(msg);
            System.Diagnostics.Debug.WriteLine(msg);
        }
        public async void Disconnect()
        {
            Connection.Stop();
        }
        

        bool sent_one_email_on_no_connection = false;
        public async void Connect()
        {
            
           
            Connection = new HubConnection(_full_server);
            HubProxy = Connection.CreateHubProxy("MyHub");
            Connection.Closed += Connection_Closed;
            
            Connection.StateChanged += Connection_StateChanged;

            try
            {
                Connection.Headers.Add("machine", Environment.MachineName.ToUpper());
                Connection.Headers.Add("ip", UtilsLib.Network.GetLocalIPAddress());
                Connection.Headers.Add("username", Environment.UserName);
                Connection.Credentials = CredentialCache.DefaultCredentials;
                Connection.EnsureReconnecting();
                Connection.Start().Wait();
            }
            catch (Exception n)
            {
                if (!sent_one_email_on_no_connection)
                {
                    UtilsLib.Error.SendDefaultError(n, "BatSignal", "Unable to open connection....", true);
                }

                sent_one_email_on_no_connection  = true;
                return;
            }
            return;
        }

        public event EventHandler NewMessage;

        public async void SendCave(string message)
        {
            InvokeGeneric<string>("BatSignal", message);
            
        }




        public async void SendGeneric(AlertHelper ah)
        {
            InvokeGeneric<AlertHelper>("GenericAlert", ah);
        }

        private List<string> groups = new List<string>();
        public async void GroupSubscribe(string group)
        {
            if (!groups.Contains(group))
                groups.Add(group);
            InvokeGeneric<string>("GroupSubscribe", group);
            
        }
        public async void GroupunSubscribe(string group)
        {
            if (groups.Contains(group))
                groups.Remove(group);
            InvokeGeneric<string>("GroupunSubscribe", group);
            
        }

        public async void DumpConnections()
        {
            InvokeGeneric<string>("DumpConnections", Environment.UserName.ToUpper());
        }

        public async void UpdateAsset(AssetUpdateHelperSignal ah)
        {
            InvokeGeneric<AssetUpdateHelperSignal>("UpdateAsset", ah);
        }


        public async void Restart(string group,int seconds)
        {
            BatSignalLib.Classes.RestartHelper rh = new BatSignalLib.Classes.RestartHelper();
            rh.group = group;
            rh.seconds = seconds;
            InvokeGeneric<BatSignalLib.Classes.RestartHelper>("Restart",rh);
            
        }

        

        
        


        public async void InvokeGeneric<T>(string header, T obj)
        {
            AddLog("Attempting to send message: " + header);
            bool success = false;
            try
            {
                if (Connection.State == ConnectionState.Connected)
                {
                    HubProxy.Invoke(header, obj);
                    success = true;

                }
                else
                {

                }
            }
            catch (Exception n)
            {
                AddLog("Message Failed (" + header + ") - " + n.Message);
            }
            finally
            {
                if(!success)
                    SendSignalRException();
            }


        }

        public void SendSignalRException()
        {
            string executing = System.Reflection.Assembly.GetEntryAssembly().Location;
            string app = System.IO.Path.GetFileNameWithoutExtension(executing);
            UtilsLib.Mail m = new UtilsLib.Mail(null, CommonInterfaces.Constants.SMTP_SERVER, null, null);
            string body = string.Join(Environment.NewLine, log);
            m.SendSMTPMail(CommonInterfaces.Constants.ERROR_EMAIL, null, null, $"[{app}] SignelR Exception....", body,
                null, false, true, null , System.Net.Mail.MailPriority.High);
        }



        public void HookUpEvent<T, Y>(string eventName, Action<T, Y> on_event)
        {
            HubProxy.On<T, Y>(eventName, on_event);
            
        }
        public void HookUpEvent<T>(string eventName, Action<T> on_event)
        {
            HubProxy.On<T>(eventName, on_event);
        }



        public void DoMessage(string msg)
        {

        }

        public Nullable<DateTime> last_disconnect;
        public static int RECONNECT_RETRY_SEC = 60;


        private Timer _reconnect;
        public bool initial_connection_try = true;
        
        private void Connection_StateChanged(StateChange obj)
        {
            string msg = $"SignalR: {obj.OldState} -> {obj.NewState}";
            AddLog(msg);

            if (obj.NewState == ConnectionState.Disconnected)
            {
                
                
                last_disconnect = DateTime.Now;
                if (null == _reconnect || _reconnect.Enabled == false)
                {
                    _reconnect = new Timer(RECONNECT_RETRY_SEC * 1000);
                    _reconnect.AutoReset = true;
                    _reconnect.Elapsed += _reconnect_Elapsed;
                    _reconnect.Start();
                }
            }
            else if (obj.NewState == ConnectionState.Connected)
            {
                sent_one_email_on_no_connection = false;
                if (null != _reconnect)
                    _reconnect.Stop();
                else
                {
                    foreach (string group in groups)
                    {
                        GroupSubscribe(group);
                    }
                }
                
            }

        }

        private void _reconnect_Elapsed(object sender, ElapsedEventArgs e)
        {
            this.Connect();
            if (Connection.State == ConnectionState.Connected)
            {
                foreach (string group in groups)
                {
                    this.GroupSubscribe(group);
                }
            }
        }

        private void Connection_Closed()
        {
            
        }
    }

}


--- FILE: BatSignalLib\MainHub.cs ---
using Task = System.Threading.Tasks.Task;
namespace BatSignalLib
{
    public partial class Server
    {
        public class MyHub : Hub
        {


            public void WriteLog(string type,string message)
            {
                string format = $"[{DateTime.Now:MM/dd/yyyy hh:mm}] - {Context.CurrentUserName()} - {type} - {message}";
                Console.WriteLine(format);
            }
            public void Send(string name, string message)
            {
                
                WriteLog("Message Received", message);
                Clients.All.addMessage(name, message);
            }

            public void AppRunner(string name, string file)
            {
                
                WriteLog("AppRunner Request Received", file);
                Process p = new Process();
                p.StartInfo.FileName = file;
                p.Start();
                Clients.Group("AppRunner").SendMessage("T");
            }


            public void RunScheduledTask(string task_name)
            {
                WriteLog("Scheduled Task Run Request", task_name);
                using (TaskService tasksrvc = new TaskService())
                {       
                    Microsoft.Win32.TaskScheduler.Task task = tasksrvc.FindTask(task_name);
                    if(null != task)
                        task.Run();
                }   
            }

            public void DumpConnections(string group)
            {
                Console.WriteLine();
                Console.WriteLine();
                List<BatSignalLib.Classes.Users> users = new List<BatSignalLib.Classes.Users>();

                foreach (var s in ConnectionManager.GetInstance())
                {
                    var user = new BatSignalLib.Classes.Users() { user_id = s.Value.user_id, connection_id = s.Value.connection_id, connection_time = s.Value.connect_time};
                    string msg = $"[{s.Value.connect_time}] - {s.Value.user_id}";
                    Console.WriteLine(msg);
                    users.Add(user);
                }
                Console.WriteLine();
                Console.WriteLine("Total: " + ConnectionManager.GetInstance().Count());
                Console.WriteLine();


                WriteLog($"User Dump Requested", null);
                
                if (null != group)
                {
                    
                    
                    {
                        Clients.Group(group).DumpConnectionHandle(users);
                    }
                }
                else
                    Clients.All.DumpConnectionHandle(users);


            }

            public void UpdateAsset(AssetUpdateHelperSignal ah)
            {
                if (null != ah.group)
                {
                    string tickers = String.Join(",", ah.assets);
                    WriteLog($"Update Asset Alert Received [{ah.assets.Count}] ({ah.group})", tickers);
                    
                    {
                        Clients.Group(ah.group).UpdateAsset(ah);
                    }
                }
                else
                    Clients.All.UpdateAsset(ah);
            }

            public void BatSignal(string message)
            {
                WriteLog("BATSIGNAL Received", message);
                
                Clients.All.BatSignal(message);
            }

  
            public void Restart(Classes.RestartHelper rh)
            {
                WriteLog("RESTART Signal Received", rh.group);
                if(String.IsNullOrWhiteSpace(rh.group))
                    Clients.All.Restart(rh);
                else
                    Clients.Group(rh.group).Restart(rh.seconds);
            }
            public void GenericAlert(AlertHelper ah)
            {
                
                
                

                if (null != ah.groups && ah.groups.Count > 0)
                {
                    string all_groups = String.Join(",", ah.groups);
                    WriteLog($"Generic Alert Received ({all_groups})", ah.message);
                    foreach (string group in ah.groups)
                    {
                        Clients.Group(group).GenericAlert(ah);
                    }
                }
                else
                    Clients.All.GenericAlert(ah);
            }

            public void GroupSubscribe(string group)
            {
                group = group.ToUpper();
                WriteLog("Subscription Request", group);
                
                Groups.Add(Context.ConnectionId, group);
            }

            public void GroupunSubscribe(string group)
            {
                group = group.ToUpper();
                WriteLog("UnSubscribe Request", group);
                
                Groups.Remove(Context.ConnectionId, group);
            }



            public override Task OnConnected()
            {
                
                string user = Context.CurrentUserName();
                Groups.Add(Context.ConnectionId, user);
                Clients.Caller.hubReceived("Welcome " + user+ "!");

                ConnectionManager.UserConnection conn = new ConnectionManager.UserConnection();
                conn.connection_id = Context.ConnectionId;
                conn.connect_time = DateTime.Now;
                conn.user_id = user;
                if(!ConnectionManager.GetInstance().ContainsKey(conn.connection_id))
                    ConnectionManager.GetInstance().Add(Context.ConnectionId,conn);
                
                WriteLog("Client Connected", user);
                return base.OnConnected();
            }
            public override Task OnDisconnected(bool stopCalled)
            {
                string user = Context.CurrentUserName();
                WriteLog("Client Disconnected", user);
                if (ConnectionManager.GetInstance().ContainsKey(Context.ConnectionId))
                    ConnectionManager.GetInstance().Remove(Context.ConnectionId);
                    
                
                return base.OnDisconnected(stopCalled);
            }
        }
    }
}


--- FILE: BatSignalLib\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("SignalRLib")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("SignalRLib")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2018")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("886c9715-1da1-49d4-a559-f2d8c96eaa95")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: BatSignalLib\Server.cs ---
namespace BatSignalLib
{
    public partial class Server
    {
        public static void StartService(string url)
        {

            

            
            WebApp.Start(url);
            
            {

                Console.WriteLine("Server running on {0}", url);
                CallingClass(url);
            }
        }


        public static void CallingClass(object o)
        {
            if (null == o || !(o.ToString().Contains("zzzzzzzzzzz")))
                return;
            Microsoft.Owin.Host.HttpListener.OwinHttpListener h = (Microsoft.Owin.Host.HttpListener.OwinHttpListener)o;
            System.Web.Cors.CorsResult i = (System.Web.Cors.CorsResult)o;
            Newtonsoft.Json.Bson.BsonObjectId j = (Newtonsoft.Json.Bson.BsonObjectId)o;
            string t = i.ToString();
            string z = j.ToString();
        }
    }

    
    class Startup
    {
        public void Configuration(IAppBuilder app)
        {           
            app.UseCors(CorsOptions.AllowAll);
            app.MapSignalR();
            ConfigureAuth(app);
        }

        private void ConfigureAuth(IAppBuilder app)
        {
            object listener;
            if (app.Properties.TryGetValue(typeof(HttpListener).FullName, out listener))
            {
                ((HttpListener)listener).AuthenticationSchemes = AuthenticationSchemes.IntegratedWindowsAuthentication;
            }
        }
    }


   
}


--- FILE: BatSignalLib\Utils.cs ---
namespace BatSignalLib
{
    public class Utils
    {
        public static string CalcTraderAlertGroup(string product)
        {
            string trading_group = $"TRADERS-{product}";
            return trading_group;
        }
    }
}


--- FILE: BatVoice\BatVoice\Program.cs ---
namespace SpeechRecognitionApp
{
    class Program
    {
        static void Main(string[] args)
        {

            
            using (
            SpeechRecognitionEngine recognizer =
              new SpeechRecognitionEngine(
                new System.Globalization.CultureInfo("en-US")))
            {

                
                recognizer.LoadGrammar(new DictationGrammar());

                
                recognizer.SpeechRecognized +=
                  new EventHandler<SpeechRecognizedEventArgs>(recognizer_SpeechRecognized);

                
                recognizer.SetInputToDefaultAudioDevice();

                
                recognizer.RecognizeAsync(RecognizeMode.Multiple);

                
                while (true)
                {
                    Console.ReadLine();
                }
            }
        }

        
        static void recognizer_SpeechRecognized(object sender, SpeechRecognizedEventArgs e)
        {
            Console.WriteLine("Recognized text: " + e.Result.Text);
        }
    }

}


--- FILE: BatVoice\BatVoice\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("BatVoice")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("")]
[assembly: AssemblyProduct("BatVoice")]
[assembly: AssemblyCopyright("Copyright ©  2020")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("7cab8762-4038-456d-9c65-9de6ec160660")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: AssetUpdater\AssetUpdater\Program.cs ---
namespace AssetUpdater
{
    class Program
    {
        [STAThread]
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            Console.WriteLine("Grabbing Assets...");
            string server = args["server"];
            string sql = args["sql"];
            bool randomize = args.ContainsFlag("randomize");
            int max = args.ContainsFlag("assets") ? System.Convert.ToInt32(args["assets"]) : -1;
            List<string> tickers = GetMissingTickers(server, sql);
            bool do_bbg = args.ContainsFlag("bbg");
            bool do_clo = args.ContainsFlag("clo");
            bool do_remits = args.ContainsFlag("remits");
            
            ETA eta = new ETA(tickers.Count, Console.WriteLine);
            tickers.Shuffle();
            if (max != -1 && tickers.Count > max)
            {
                tickers.RemoveRange(max, tickers.Count - max);
            }
            tickers.Shuffle();

            
            foreach(string ticker in tickers)
            {
                try
                {
                    if (do_bbg)
                    {
                        Assets.MT.InsertUpdateIfNeeded(server, ticker, false, false,null);
                    }
                    if(do_clo)
                    {
                        Assets.MT.GetOCTerminalData(server, ticker);
                    }
                    if(do_remits)
                    {
                        DateTime asOf = DateTime.Today.FirstDayOfMonth();
                        Assets.MT.ProcessRemits(server, ticker, asOf);
                    }

                    eta.IncrementAndReport();
                }catch(Exception n)
                {
                    Console.WriteLine("Crashed...moving on");
                }
            }
            if (args.ContainsFlag("to"))
            {
                Mail m = new Mail(null, null, null, null);
                string body = String.Join(Environment.NewLine, tickers);
                m.SendMail(args["to"], null, null, "Bloomberg Updated Assets: " + tickers.Count, body, null, false,true,null);
            }
        }

        public static List<string> GetMissingTickers(string server,string sql)
        {
            Query q = new Query(sql, server);
            List<string> tickers = q.ExecuteList<string>();
            return tickers;
        }
    }
}


--- FILE: AssetUpdater\AssetUpdater\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("AssetUpdater")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("AssetUpdater")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2017")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("4993c88f-a474-403f-95d0-ae7f305acd29")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: AssetUpdater\AssetUpdater\SQL\CLOAssets.sql ---
select
  max(ticker) [ticker]
  , deal_name 
  from 
    assets 
    where 
      bond_label_1  = 'CDO/CLO' 
      and collat_type LIKE '%CLO%'
      and deal_name is not null 
	  and oc_unavailable is null
    group by deal_name


--- FILE: AssetUpdater\AssetUpdater\SQL\DailyPosition.sql ---
select distinct bh.cusip 
  from 
    BetaHistory bh
    left join Assets a on a.cusip = bh.cusip
    where
      bh.acct_no in (5258,5264,5261,5172)
      and bh.ProcessingTradeDate = dbo.PreviousBday(dbo.Today())
      and a.cusip is null and bh.cusip is not null


--- FILE: AssetUpdater\AssetUpdater\SQL\FindAssets.sql ---
create table #tickers
(
  ticker varchar(35)
)

select distinct bwd.ticker
  from
    BWICs b
    join dbo.BWICDetail bwd ON bwd.bwic_id = b.id
    left join Assets a on a.ticker = bwd.ticker
    left join InvalidTickers it on bwd.ticker = it.ticker
  where
    b.bid_time > DATEADD(D, -7, GetDate())
    and a.ticker is null or a.bbg_id is null
    and it.ticker is null
 
drop table #tickers


--- FILE: AssetUpdater\AssetUpdater\SQL\NeededRemits.sql ---
declare @account int
declare @asOf date
declare @eom date
declare @bom date


select @asOf = dbo.PreviousBday('6/30/2017')
select @eom=dbo.LastBdayOfMonth(dateadd(m,-1,@asOf))
select @BOM=daTEADD(month, DATEDIFF(month, 0, @asOf), 0)

select 
  acct_no
  , dbo.Trim(b.cusip) [cusip]
  , cur_qty [eom_position]
  , b.mkt_price [eom_mark]
  , b.cur_accr_int_amt
  , processingTradeDate [asOf]
  into #eom
  from 
    BetaHistory b 
    join Assets a on a.cusip = b.cusip
    where 
    processingTradeDate = @eom
    and acct_no in (5258,5268,5264,5261,5262)
    AND t_or_s_IND = 'S'
    AND cur_qty != 0
    and a.market_sector != 'Govt'
    
   
    

	select 
    distinct 
      e.cusip 
    from 
        #eom e
    join Assets a on a.cusip = e.cusip
    left join Remits r on a.ticker = r.ticker and r.remit_month = @BOM
    where
    r.remit_month is null
        

	drop table #eom


--- FILE: AssetUpdater\AssetUpdater\SQL\NormalUpdates.sql ---
EXEC DBO.GetNextBBGUpdates


--- FILE: AssetUpdater\AssetUpdater\SQL\UpcomingCLO.sql ---
select max(bwd.ticker) [ticker],deal_name,max(bid_time) [bid_time]
  from 
    BWICS b
    join BWICDetail bwd on b.id = bwd.bwic_id
    join Assets a on a.ticker = bWD.ticker
    where
    b.bid_time >= dateadd(wk,-1,GetDate())
    and a.collat_type like '%CLO%'
	and oc_unavailable is null
    group by deal_name
    order by bid_time desc


--- FILE: Assets\Analytics.cs ---
namespace Assets
{
    public class Analytics
    {

        public static RollAnalysis RA(string cusip, double oface, double cface, double price, double finance_rate,
            double cpr, DateTime buy_settle, DateTime sell_settle)
        {

            if (finance_rate > 1)
                finance_rate = finance_rate / 100.0;

            double days_in_year = 359.637465585898;
            double? buy_accrued_int = -Trade.AccruedInterestCPR(cusip, oface, buy_settle, buy_settle, 0);
            double? sell_accrued_int = Trade.AccruedInterestCPR(cusip, oface, buy_settle, sell_settle, cpr);
            double buy_factor = BloombergLib.Bloomberg.GetInstance().GetData<double>(cusip, "MTG_FACTOR_SET_DT",
                "SETTLE_DT=" + buy_settle.ToString("yyyMMdd"));
            double buy_cface = buy_factor * oface;
            double total_principal =
                Cashflows.TotalPrincipal(cusip, oface, buy_settle, cpr, sell_settle);
            double scheduled_interest =
                Cashflows.ScheduledInterest(cusip, oface, buy_settle, cpr, sell_settle);
            double future_cashflow = total_principal + scheduled_interest;
            double buy_market_value = cface * price / 100.0;
            double days = (sell_settle - buy_settle).TotalDays;
            double finance_charge = -(buy_market_value * (finance_rate / days_in_year) * days);

            double ending_balance = cface - total_principal;
            
            double buy_total_proceeds = buy_market_value - buy_accrued_int.Value;
            double solve_for_clean_mv = buy_total_proceeds - future_cashflow - sell_accrued_int.Value - finance_charge;
            double roll_price = solve_for_clean_mv / ending_balance * 100.00;
            
            double drop_in_dec = (roll_price - price);
            double drop_in_tics = drop_in_dec * 32.0;
            double cpn = Trade.AccruedCpn(cusip, sell_settle).Value;
            double? eom_accrued = cpn / 12.0 * buy_cface;
           RollAnalysis ra = new RollAnalysis
            {
                
                remit_principal = total_principal,
                remit_interest = scheduled_interest,
                funding_cost = finance_charge,
                price = roll_price,
                drop_in_tics = drop_in_tics,
                drop_in_dec = drop_in_dec,
                eom_accrued = eom_accrued.Value,
                buy_accrued_int = buy_accrued_int.Value,
                sell_accrued_int = sell_accrued_int.Value,
                sell_accrued_int_eom = eom_accrued.Value, 
                drop_due_to_principal = (-((price+drop_in_dec)/100.0)+1) * total_principal
            };
            return ra;
        }

        public class RollAnalysis
        {
            
            public double remit_principal;
            public double remit_interest;
            public double remit_total
            {
                get { return remit_principal + remit_interest;  }
            }
            public double total_interest
            {
                get { return remit_interest + net_accrued_int;  }
            }
            public double total_net_interest
            {
                get { return remit_interest + net_accrued_int + funding_cost;  }
            }
            public double funding_cost;
            public double drop_in_tics;
            public double drop_in_dec;
            public double price;
            public double eom_accrued;
            public double buy_accrued_int;
            public double sell_accrued_int;
            public double sell_accrued_int_eom;
            public double drop_due_to_principal;
            public double total_net_interest_eom
            {
                get { return buy_accrued_int + remit_interest + funding_cost + eom_accrued; }
            }

            public double net_accrued_int_eom
            {
                get { return buy_accrued_int + eom_accrued; }
            }
            public double net_accrued_int
            {
                get { return buy_accrued_int + sell_accrued_int; }
            }
        }

        public static int WriteAnalytics(string server, Nullable<int> analytics_id_existing, DateTime asOf, string ticker, string bond_input, double? oface, string px_input, double? cface, string settle_input, string rates_input, double? oas, double? yield, double? i_spread, double? price, double? duration_eff, double? convexity_eff, double? pdur_2yr, double? pdur_5yr, double? pdur_10yr, double? pdur_30yr, string bbg_type, double? bbg_cpn, string bbg_collat_type, double? bbg_med, double? bbg_wal, double? bbg_price, double? bbg_300, double? bbg_yield, double? bbg_i_spread, double? bbg_z_spread, double? bbg_wam, double? bbg_wala, double? bbg_als, double? bg_mals, double? bbg_CPR_1M, double? bbg_CPR_3M, double? bbg_CPR_6M, double? bbg_CPR_12M, double ct2, double ct5, double ct10, double ct30, double fncl_cc)
        {
            string sql = "exec dbo.InsertUpdateAnalytics @analytics_id_existing=@analytics_id_existing, @asOf=@asOf,@ticker=@ticker,@bond_input=@bond_input,@oface=@oface,@px_input=@px_input,@cface=@cface,@settle_input=@settle_input,@rates_input=@rates_input,@oas=@oas,@yield=@yield,@i_spread=@i_spread,@price=@price,@duration_eff=@duration_eff,@convexity_eff=@convexity_eff,@pdur_2yr=@pdur_2yr,@pdur_5yr=@pdur_5yr,@pdur_10yr=@pdur_10yr,@pdur_30yr=@pdur_30yr,@bbg_type=@bbg_type,@bbg_cpn=@bbg_cpn,@bbg_collat_type=@bbg_collat_type,@bbg_med=@bbg_med,@bbg_wal=@bbg_wal,@bbg_price=@bbg_price,@bbg_300=@bbg_300,@bbg_yield=@bbg_yield,@bbg_i_spread=@bbg_i_spread,@bbg_z_spread=@bbg_z_spread,@bbg_wam=@bbg_wam,@bbg_wala=@bbg_wala,@bbg_als=@bbg_als,@bg_mals=@bg_mals,@bbg_CPR_1M=@bbg_CPR_1M,@bbg_CPR_3M=@bbg_CPR_3M,@bbg_CPR_6M=@bbg_CPR_6M,@bbg_CPR_12M=@bbg_CPR_12M, @ct2=@ct2, @ct5=@ct5, @ct10=@ct10, @ct30=@ct30, @fncl_cc=@fncl_cc, @analytics_id=@analytics_id OUTPUT";
            Query q = new Query(sql, server);
            q.AddParameter("@analytics_id_existing", analytics_id_existing);
            q.AddParameter("@asOf", asOf);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@bond_input", bond_input);
            q.AddParameter("@oface", oface);
            q.AddParameter("@px_input", px_input);
            q.AddParameter("@cface", cface);
            q.AddParameter("@settle_input", settle_input);
            q.AddParameter("@rates_input", rates_input);
            q.AddParameter("@oas", oas);
            q.AddParameter("@yield", yield);
            q.AddParameter("@i_spread", i_spread);
            q.AddParameter("@price", price);
            q.AddParameter("@duration_eff", duration_eff);
            q.AddParameter("@convexity_eff", convexity_eff);
            q.AddParameter("@pdur_2yr", pdur_2yr);
            q.AddParameter("@pdur_5yr", pdur_5yr);
            q.AddParameter("@pdur_10yr", pdur_10yr);
            q.AddParameter("@pdur_30yr", pdur_30yr);
            q.AddParameter("@bbg_type", bbg_type);
            q.AddParameter("@bbg_cpn", bbg_cpn);
            q.AddParameter("@bbg_collat_type", bbg_collat_type);
            q.AddParameter("@bbg_med", bbg_med);
            q.AddParameter("@bbg_wal", bbg_wal);
            q.AddParameter("@bbg_price", bbg_price);
            q.AddParameter("@bbg_300", bbg_300);
            q.AddParameter("@bbg_yield", bbg_yield);
            q.AddParameter("@bbg_i_spread", bbg_i_spread);
            q.AddParameter("@bbg_z_spread", bbg_z_spread);
            q.AddParameter("@bbg_wam", bbg_wam);
            q.AddParameter("@bbg_wala", bbg_wala);
            q.AddParameter("@bbg_als", bbg_als);
            q.AddParameter("@bg_mals", bg_mals);
            q.AddParameter("@bbg_CPR_1M", bbg_CPR_1M);
            q.AddParameter("@bbg_CPR_3M", bbg_CPR_3M);
            q.AddParameter("@bbg_CPR_6M", bbg_CPR_6M);
            q.AddParameter("@bbg_CPR_12M", bbg_CPR_12M);

            q.AddParameter("@ct2", ct2);
            q.AddParameter("@ct5", ct5);
            q.AddParameter("@ct10", ct5);
            q.AddParameter("@ct30", ct30);
            q.AddParameter("@fncl_cc", fncl_cc);

            q.AddParameter("@analytics_id|OUT", -1);
            q.Execute();
            int new_id = System.Convert.ToInt32(q.Parameters["@analytics_id"]);
            return new_id;
        }
    }
}


--- FILE: Assets\Asset.cs ---
namespace Assets
{

	public partial class Asset
	{
		public string asset_id { get; set; }
		public string address_1 { get; set; }
		public string address_2 { get; set; }
		public string address_full { get; set; }
		public string address_simple { get; set; }
		public string last_name { get; set; }
		public string city { get; set; }
		public string state { get; set; }
		public string zip { get; set; }
		public double investment_payment { get; set; }
		public double starting_home_value { get; set; }
		public double investment_pct { get; set; }
		public double exchange_rate { get; set; }
		public double unlock_pct
        {
            get
            {
                return investment_payment / starting_home_value * exchange_rate;
            }
        }
		public double cost_limit { get; set; }
        public double cost_limit_basis { get; set; }
        public DateTime? buyout_active_date { get; set; }
        public double home_finance_limit { get; set; }
		public DateTime effective_date { get; set; }
		public DateTime expiration_date { get; set; }
		public DateTime update_time { get; set; }
		public string update_by { get; set; }
		public string first_name_co { get; set; }
		public string first_name { get; set; }
		public string name_simple { get; set; }
		public DateTime orig_date { get; set; }
		public int owner { get; set; }
		public decimal phone_number { get; set; }
		public DateTime sign_date { get; set; }
		public string full_name { get; set; }
		public string full_name_co { get; set; }
		public string last_name_co { get; set; }
		public string email { get; set; }
		public DateTime settle_date { get; set; }
		public string middle_name { get; set; }
		public string middle_name_co { get; set; }
		public string ssn_last4 { get; set; }
		public string ssn_last4_co { get; set; }
		public string apn { get; set; }
		public int fips { get; set; }
        public int term_months { get; set; }
        public double current_home_value { get; set; }

        public void PopulateAsset(string asset_id, DateTime effective_date, double starting_home_value, double cost_limit, double cost_limit_basis, DateTime? buyout_active_date, double investment_payment, double exchange_rate,int term_months,double current_home_value)
        {
            this.asset_id = asset_id;
            this.effective_date = effective_date;
            this.starting_home_value = starting_home_value;
            this.current_home_value = current_home_value;
            this.cost_limit = cost_limit;
            this.cost_limit_basis = cost_limit_basis;
            this.buyout_active_date = buyout_active_date;
            this.investment_payment = investment_payment;
            this.exchange_rate = exchange_rate;
            this.term_months = term_months;
        }

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


    }
}


--- FILE: Assets\Cashflows.cs ---
namespace Assets
{
    public class Cashflows
    {
        
         
        public static DataTable GenerateCashflows(string ticker, double oface,  DateTime settle_1, double cpr)
        {

            DateTime first_settle = BloombergLib.Bloomberg.GetInstance().GetData<DateTime>(ticker + " mtge", "FIRST_SETTLE_DT");
            if (first_settle > settle_1)
                settle_1 = first_settle;
            Dictionary<string, string> over = new Dictionary<string, string>();
            over.Add("MTG_PREPAY_SPEED", cpr.ToString());
            over.Add("MTG_PREPAY_TYP", "CPR");
            over.Add("CASHFLOW_AS_OF_DATE", settle_1.SetDay(1).ToString("yyyyMMdd"));
            over.Add("MTG_FACE_AMT", oface.ToString());
            over.Add("SETTLE_DT", settle_1.ToString("yyyyMMdd"));
            over.Add("YLD_FLAG", "1"); 
            DataTable cashflows = (DataTable) BloombergLib.Bloomberg.GetInstance()
                .GetDataBulk(ticker + " @BVAL mtge", "MTG_CASH_FLOW", over).Rows[0]["MTG_CASH_FLOW"];

            

            
            return cashflows;

        }
        public static double ScheduledInterest(string ticker, double oface, DateTime settle_1,double cpr,DateTime month_to_pick_flow_from)
        {
            return Cashflows.GetSingleCashflowNumber<double>("INTEREST",ticker, oface, settle_1, cpr, month_to_pick_flow_from);
        }

        public static double TotalPrincipal(string ticker, double oface, DateTime settle_1,double cpr,DateTime month_to_pick_flow_from)
        {
            return Cashflows.GetSingleCashflowNumber<double>("PRINCIPAL PAID",ticker, oface, settle_1, cpr, month_to_pick_flow_from);
        }
        public static double? ScheduledBalance(string ticker, double oface, DateTime settle_1,double cpr, DateTime? pick_cashflow = null)
        {
            if ((null != ticker && ticker.Substring(0,2).ToUpper() == "T ") || null == oface || oface == 0)
                return null;
            return Cashflows.GetSingleCashflowNumber<double>("PRINCIPAL BALANCE",ticker, oface, settle_1, cpr,pick_cashflow);
        }

        public static T GetSingleCashflowNumber<T>(string return_column,string ticker, double oface, DateTime buy_settle, double cpr, DateTime? pick_cashflow = null)
        {
            DataRow row = GetSingleCashflowRow(ticker, oface, buy_settle, cpr, pick_cashflow);
            if (null == row)
                return (T) System.Convert.ChangeType(0,typeof(T));
            return (T) System.Convert.ChangeType(row[return_column],typeof(T));
        }
        public static DataRow GetSingleCashflowRow(string ticker, double oface, DateTime buy_settle, double cpr, DateTime? pick_cashflow = null)
        {
            DataTable cashflows = GenerateCashflows(ticker, oface, buy_settle, cpr);
            if(cashflows.Rows.Count == 0)
                return null;
            if (null != pick_cashflow)
            {
                foreach (DataRow row in cashflows.Rows)
                {
                    
                    DateTime date = System.Convert.ToDateTime(row["PAYMENT DATE"]);
                    if(date.SameMonth(pick_cashflow.Value))
                        return row;
                }
            }

            return null;
        }

    }
}


--- FILE: Assets\Collat.cs ---
namespace Assets
{
    public class Collat
    {
        public static bool WriteHPI(string server, int zip, DateTime date, Nullable<int> value, int? region_id, int? size_rank, string state, string city, string metro, string county)
        {
            if (null == value)
                return false;
            
            
            
            
            Query q = GetHPIQuery(server, zip, date, value, region_id, size_rank, state, city, metro, county);
            q.Execute();
            return true;
        }

        public static string GetRawHPISQL(string property_type,string region_type,int? zip, DateTime date, Nullable<int> value, int? region_id, int? size_rank, string state, string city, string metro, string county)
        {
            string pad_zip = null;
            if(null != pad_zip)
                pad_zip = $"{zip:00000}".ToString();
            string sql = $"insert into LoanPerformance..HPI (zip,region_type,property_type,zip_pad,asOf,value,region_id,size_rank,state,city,metro,county) values ('{zip}','{region_type.ToUpper()}','{property_type.ToUpper()}','{pad_zip}','{date:MM/dd/yyyy}',{value},{region_id},{size_rank},'{state}','{city}','{metro}','{county}')";
            return sql;
        }

        public static Query GetHPIQuery(string server, int zip, DateTime date, Nullable<int> value, int? region_id, int? size_rank, string state, string city, string metro, string county)
        {
            string pad_zip = $"{zip:00000}".ToString();
            string sql = "insert into HPI (zip,zip_pad,asOf,value,region_id,size_rank,state,city,metro,county) values (@zip,@pad_zip,@date,@value,@region_id,@size_rank,@state,@city,@metro,@county)";

            Query q = new Query(sql, server);

            
            {
                q.AddParameter("@zip", zip);
                q.AddParameter("@pad_zip", pad_zip);
                q.AddParameter("@date", date);
                q.AddParameter("@value", value);
                q.AddParameter("@region_id", region_id);
                q.AddParameter("@size_rank", size_rank);
                q.AddParameter("@state", state);
                q.AddParameter("@city", city);
                q.AddParameter("@metro", metro);
                q.AddParameter("@county", county);
            }
            
            return q;
        }
        public static Query GetZillowSQL(string server, int hpitype_id,int zip, string date_string, Nullable<double> value)
        {
            if (null == value)
                return null;
            
            
            string zip_pad = $"{zip:00000}".ToString();
            DateTime asOf;
            if (DateTime.TryParse(date_string, out asOf))
            {
                asOf = asOf.SetDay(1);
            }
            if(null == asOf)
            {

            }
            string sql = $"insert into HPI (hpitype_id,zip,zip_pad,asOf,value) values (@hpitype_id,@zip,@zip_pad,@asOf,@value)";
            Query q = new Query(sql, server);
            q.UseCache = true;
            q.AddParameter("@zip", zip);
            q.AddParameter("@zip_pad", zip_pad);
            q.AddParameter("@asOf", asOf);
            q.AddParameter("@value", value);
            q.AddParameter("@hpitype_id", hpitype_id);
            
            return q;
        }

        public static string GetZillowSQLTxt(string server, int hpitype_id, int zip, string date_string, Nullable<double> value)
        {
            if (null == value)
                return null;
            
            
            string zip_pad = $"{zip:00000}".ToString();
            DateTime asOf;
            if (DateTime.TryParse(date_string, out asOf))
            {
                asOf = asOf.SetDay(1);
            }
            if (null == asOf)
            {

            }
            string sql = $"insert into HPI (hpitype_id,zip,zip_pad,asOf,value) values ({hpitype_id},'{zip}','{zip_pad}','{asOf}',{value})";
            return sql;
        }
        public static string GetZillowBCP(string server, int zip, string date_string, Nullable<int> value)
        {
            if (null == value)
                return null;
            int year = Convert.ToInt32(date_string.Split('-')[0]);
            int month = Convert.ToInt32(date_string.Split('-')[1]);
            DateTime date = new DateTime(year, month, 1);
            string sql = $"{zip}\t{date:M/d/yyyy}\t{value}".Trim();
            
            
            
            
            
            
            return sql;
        }
        public static Nullable<double> CalcNewAppraisal(string server, Nullable<double> orig_appraisal_amt, DateTime start_date, int hpitype_id,int zip, string state, Nullable<DateTime> cutoff)
        {
            if (null == orig_appraisal_amt)
                return null; ;

            Nullable<double> appreciation = GetAppreciationRate(server, hpitype_id, state, zip, start_date, cutoff);

            if (null == appreciation)
                return null;

            return (1.0 + appreciation.Value) * orig_appraisal_amt.Value;

        }

        public static Nullable<double> GetAppreciationRate(string server, int hpitype_id,string state, int zip, DateTime orig, Nullable<DateTime> cutoff)
        {
            if (String.IsNullOrEmpty(state))
                state = "USA";

            if (null == cutoff)
                cutoff = new DateTime(2022, 5, 1);

            Nullable<double> zillow = GetZillowHIPAppreciation(server, hpitype_id,zip, orig, cutoff);
            if (null != zillow)
                return zillow;

            
            
            

            

            
            

            return null;

        }

        public static bool HPIExists(string server, int hpitype_id,int zip,DateTime asOf)
        {
            var l = HPIList(server,hpitype_id,zip);
            return l.Contains(asOf);

        }

        public static List<DateTime> HPIList(string server, int hpitype_id, int zip)
        {
            string sql = "select asof from HPI where zip = @zip and hpitype_id=@hpitype_id";
            Query q = new Query(sql, server);
            q.AddParameter("@zip", zip);
            q.AddParameter("@hpitype_id", hpitype_id);
            q.UseCache = false;
            List<DateTime> l = q.ExecuteList<DateTime>("asOf");
            return l;

        }

        public static Nullable<double> GetZillowHIPAppreciation(string server, int hpitype_id,int zip, DateTime orig, Nullable<DateTime> cutoff)
        {
            if (null == cutoff)
                cutoff = new DateTime(2018, 4, 1);


            Nullable<double> begin = GetHPIValue(server, hpitype_id, orig, zip);
            Nullable<double> end = GetHPIValue(server, hpitype_id,cutoff.Value, zip);

            return CalcAppreciation(begin, end);

        }
        public static Nullable<double> GetHPIValue(string server,int hpitype_id, DateTime date, int zip)
        {

            date = date.SetDay(1);
            string sql = "select value from HPI where asOf = @date and zip = @zip and hpitype_id=@hpitype_id";

            Query q = new Query(sql, server);
            q.AddParameter("@zip", zip);
            q.AddParameter("@date", date);
            q.AddParameter("@hpitype_id", hpitype_id);
            q.UseCache = true;
            return q.ExecuteSingleNullable<double>("value");
        }

        public static Nullable<double> CalcAppreciation(double? begin, double? end)
        {
            if (null == begin || null == end)
                return null;
            return (end.Value - begin.Value) / begin.Value;
        }


        
        
        
        
        
        

        
        

        
        
        
        

        

        
        
        
        
        
        

    }
}


--- FILE: Assets\Mapping.cs ---
namespace Assets
{
    public class Mapping
    {
        public object MapValue(string server,string value)
        {
            Dictionary<string, object> vals = GetMappingTable(server);
            if (null == maps)
                maps = GetMappingTable(server);

            if (vals.ContainsKey(value))
            {
                return vals[value];
            }
            return null;
        }

        public Mapping _mapping;
        public Dictionary<string, object> maps = new Dictionary<string, object>();
        public Mapping GetInstance()
        {
            if (null == _mapping)
            {
                _mapping = new Mapping();
            }

            return _mapping;
        }

        public static Dictionary<string, object> GetMappingTable(string server)
        {
            string sql = "SELECT raw,value from Mapping";
            Query q = new Query(sql, server);
            q.UseCache = true;
            return q.ExecuteDictRows<string,object>("raw","value");
        }
    }
}


--- FILE: Assets\MT.cs ---
namespace Assets
{
    public class MT
    {

        
        
        
        

        public static bool TickerInAssetsTable(string server,string ticker)
        {
            string sql = "select count(*) [count] from Assets where ticker = @ticker";
            if (UtilsLib.Validate.IsCusip(ticker))
                sql = "select count(*) [count] from Assets where cusip = @ticker";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker<varchar>", ticker);
            return q.ExecuteSingle<int>("count") > 0;
        }


        public static string GetTickerFromAsset(string server, string ticker, bool use_cache, string return_val = "ticker")
        {
            return GetValueFromAsset(server, ticker, use_cache, return_val);
        }
        public static string GetValueFromAsset(string server, string ticker,bool use_cache,string return_val)
        {
            string sql = "select * from Assets where ticker = @ticker or ticker_short=@ticker";
            if (!ticker.Contains(" "))
            {
                if (UtilsLib.Validate.IsCusip(ticker) || ticker.Length == 8)
                    sql = "select * from Assets where cusip = @ticker or (len(@ticker)=8 and cusip like '" + ticker + "%')";
                else if (UtilsLib.Validate.IsISIN(ticker) || ticker.Length == 9)
                    sql = "select * from Assets where isin = @ticker or (len(@ticker)=9 and isin like '%" + ticker + "')";
            }
            Query q = new Query(sql, server);
            q.AddParameter("@ticker<varchar>", ticker);
            q.UseCache = use_cache;
            return q.ExecuteSingle<string>(return_val);
        }

        public class LoadHelper
        {
            public bool all_loaded;
            public List<string> all_tickers = new List<string>();
            public int inserted_bonds;
        }

        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        


        public static void CopyAssetHistory(string server, string ticker, Nullable<DateTime> asOf)
        {
            string sql = "exec dbo.CopyAssetHistory @ticker=@ticker,@asOf=@asOf";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@asOf", asOf);
            q.Execute();
        }
       
       
       
       
       
       
       
       

       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
       
                        
       
       
       
       
       
       
                    
       
       
       
       
       
       
       
       
       
       
       
       
       
       

        public static List<string> GetTickersFromDeal(string server, List<string> deal_name_or_ticker)
        {
            
            string sql = "exec dbo.GetTickersForDeal @raw=@raw";
            Query q = new Query(sql, server);
            q.AddParameter("@raw", deal_name_or_ticker);
            DataSet set = q.Execute();
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            List<string> tickers = set.Tables[0].ToList<string>("ticker");
            return tickers;
        }

        public static void MarkAllTranchesLoaded(string server, string deal_name,int tranches_in_deal)
        {
            string sql = "update Assets set all_tranches=1, tranches_in_deal=@tranches_in_deal where deal_name = @deal_name";
            Query q = new Query(sql, server);
            q.AddParameter("@deal_name", deal_name);
            q.AddParameter("@tranches_in_deal", tranches_in_deal);
            q.Execute();
        }

        
        
        
        
        
        
        
        
        
        
           
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        public static bool RecordExists(string server, string ticker,DateTime remit_month)
        {
            remit_month = remit_month.FirstDayOfMonth();
            string sql = "select * from Remits where ticker = @ticker and remit_month=@remit_month";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@remit_month", remit_month);
            return (q.ExecuteTable().Rows.Count != 0);
        }
        public static void InsertUpdateCashFlow(string server, string ticker, DateTime remit_month,double coupon,double interest,double principal,double balance)
        {
            string sql = "exec dbo.InsertUpdateRemit @ticker=@ticker, @remit_month=@remit_month, @coupon=@coupon, @interest=@interest, @principal=@principal, @balance=@balance";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@remit_month", remit_month);
            q.AddParameter("@coupon", coupon);
            q.AddParameter("@interest", interest);
            q.AddParameter("@principal", principal);
            q.AddParameter("@balance", balance);
            q.Execute();
        }

        public class AssetUpdateHelper
        {
            public bool updated;
            public int asset_insert_count;
            public Dictionary<string, string> tickers = new Dictionary<string, string>();
        }

        
        
        
        
        

        
        
        
        
        
        

        
        
        
        
        
        

        
        

        

 

        
        
        
        

        
        
        

        
        
        
        
        
        
        


        
        

        
        
        
        
        
        

        
        
        
        


        
        
        
        


        
        
        
        
        
        
        


        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        public static Query GetAssetCacheQuery(string server,string asset,string field)
        {
            string sql = "select * from Assets where ticker = @ticker";
            bool is_cusip = UtilsLib.Validate.IsCusip(asset);
            bool is_isin = UtilsLib.Validate.IsISIN(asset);
            bool is_figi = UtilsLib.Validate.IsBBGID(asset);
            if (is_cusip && !is_isin)
                sql = "select * from Assets where cusip = @ticker";
            if(is_isin) 
                sql = "select * from Assets where (isin = @ticker or isin like '%" + asset +"%')";
            if (is_figi)
                sql = "select * from Assets where bbg_id = @ticker";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker<varchar>", asset);
            q.UseCache = true;
            return q;
        }

        public class LastUpdateHelper
        {
            public Nullable<DateTime> LastUpdate = null;
            public bool JustAdded = false;
            public object _o = null;
            
            
            
            
        }

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        


        
        
        
        
        
        
        

        
        
        
        
        

        
        
        
        
        

        
        
        
        


        
        

        

        
        
        
        
        

        
        

        
        
        
        
        
        
        
        
        
        

        
        

        
        
        
        
        
        

        
        
        
        
        
        

        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        

        
        
        

        
        




        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        

        
        

        
        


        
        
        
        
        

        
        
        
        
        
        
        

        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        

        
        
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

        

        
        
        
        
        

        
        
        
        
        
        

        
        
        
        
        
        
        
        
        

        
        

        
        
        

        public class MSAHelper
        {
            public double houston_amt = 0;
            public double gateway_mkt = 0;

        }

        public static MSAHelper UpdateBondMSA(string server, string ticker, DateTime asOf, DataTable tbl)
        {
            bool exists = MSAsAlreadyExists(server, ticker, asOf);
            if (exists)
                return null;
            MSAHelper m = new MSAHelper();
            List<string> gateway_msa = new List<string>
            {
                "New York-Newark - Jersey City, NY - NJ - PA",
                "Boston - Cambridge - Newton, MA - NH",
                "Chicago - Naperville - Elgin, IL - IN - WI",
                "Los Angeles-Long Beach - Anaheim, CA",
                "San Francisco-Oakland-Hayward, CA"
            };

            foreach (DataRow row in tbl.Rows)
            {
                string msa = row["METROPOLITAN STATISTICAL ARE"].ToString();
                int num_prop = System.Convert.ToInt32(row["NUMBER OF PROPERTIES"]);
                double cface = System.Convert.ToDouble(row["CURRENT ALLOCATED AMOUNT"]);
                if (msa == "Houston-The Woodlands-Sugar Land, TX")
                    m.houston_amt += cface;
                if (gateway_msa.Contains(msa))
                    m.gateway_mkt += cface;
                InsertBondMSA(server, asOf, ticker,msa, num_prop, cface);
            }
            return m;
        }



        public static bool MSAsAlreadyExists(string server, string ticker, DateTime asOf)
        {
            string sql = "exec dbo.BondMSAExists @ticker=@ticker,@asOf=@asOf, @exists=@exists|OUT OUTPUT";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@asOf", asOf);
            q.AddParameter("@exists|OUT", -1);
            DataTable tbl = q.ExecuteTable();
            bool exists = System.Convert.ToBoolean(q.Parameters["@exists"]);
            return exists;
        }

        public static void InsertBondMSA(string server, DateTime asOf, string ticker, string msa, int num_properties, Nullable<double> cface)
        {
            string sql = "insert into BondMSA (ticker,asOf,msa,num_prop,cface) values (@ticker,@asOf,@msa,@num_prop,@cface)";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@msa", msa);
            q.AddParameter("@num_prop", num_properties);
            q.AddParameter("@asOf", asOf);
            q.AddParameter("@cface", cface);
            q.Execute();
        }

        public static void DeleteFromBondMSA(string server,string ticker)
        {
            string sql = "delete from BondMSA where ticker = @ticker";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.Execute();
        }


        
        
        
        
        
        

        
        
        
        
        
        
        

        
        
        
                
        
        
        
        
        
        
        
        
        
        

        
        
                
        
        
        
        
        

        
        
        

        

        
        
            
        
        
                
        
        
        
        
        
        
        
        
        
        
        
                
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        
        
        
        
        

        
        
            
        
        
        
        
        

        
        
        
        
        
        
        
        
        
        
        
        
        

        
        
        

        


        public static void UpdateSellers(string server,string ticker,bool force)
        {
            bool exists = !force;
            if (force == false)
            {
                exists = SellerDataExists(server, ticker);
            }
            if (exists && force)
                ClearSellerData(server, ticker);
            if(!exists)
            {
                InsertSellers(server, ticker);
            }
        }

        public static void InsertSellers(string server,string ticker)
        {
            DataTable tbl = BloombergLib.Bloomberg.GetInstance().GetDataBulk(ticker, "MTG_TOP_SELLERS");
            foreach (DataRow row in ((DataTable) tbl.Rows[0][1]).Rows)
            {
                string seller = row[0].ToString();
                double upb = System.Convert.ToDouble(row[1]);
                double percentage = System.Convert.ToDouble(row[2]);
                int count = System.Convert.ToInt32(row[3]);
                string sql = "insert into HECM..Sellers (ticker,seller,upb,percentage,count) values (@ticker,@seller,@upb,@percentage,@count)";
                Query q = new Query(sql, server);
                q.AddParameter("@ticker", ticker);
                q.AddParameter("@seller", seller);
                q.AddParameter("@upb", upb);
                q.AddParameter("@percentage", percentage);
                q.AddParameter("@count", count);

                q.Execute();
            }


        }

        public static void ExpandDeal(string server, string deal)
        {
            List<string> existing_tickers = ExistingTickersFromDeal(server, deal);
            
        }

        public static List<string> ExistingTickersFromDeal(string server,string deal)
        {
            string sql = "select ticker from Assets where ticker like '" + deal + "%'";
            Query q = new Query(sql, server);
            List<string> tickers = q.ExecuteList<string>();
            return tickers;
        }
        public static void ClearSellerData(string server, string ticker)
        {
            string sql = "delete from HECM..Sellers where ticker = @ticker";
            Query q = new Query(sql, server);
            q.ExecuteTable();
        }

        public static bool SellerDataExists(string server,string ticker)
        {
            string sql = "select count(*) from HECM..Sellers where ticker = @ticker";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            int num = q.ExecuteSingle<int>();
            return num >= 1;
        }




        
        
        
            
        
        
        
        
        

        public static string InsertUpdateBondLookup(string server, string lookup, string ticker)
        {
            string sql = "exec dbo.InsertUpdateBondLookup @lookup=@lookup,@ticker=@ticker";
            Query q = new Query(sql, server);
            q.AddParameter("@lookup", lookup);
            q.AddParameter("@ticker", ticker);
            q.UseCache = true;
            string ret = q.ExecuteSingle<String>("ticker");
            if (String.IsNullOrEmpty(ret))
            {
                Database.DBCache.GetInstance().RemoveCache(q);
            }
            return ret;
        }
        public static DataTable GetRepoRates(string cusip, DateTime startDate, DateTime endDate, string repoLine)
        {
            repoLine = GetRepoFacilityId(CommonInterfaces.Constants.Database.SQL_SERVER, repoLine);

            string sql = "SELECT asOf,rate FROM [HECM].[dbo].[RepoRates] WHERE cusip = @cusip AND repofacility_id=@repoLine  AND asOf between @FromDate and @ToDate ORDER BY asOf";
            Query q = new Query(sql, CommonInterfaces.Constants.Database.SQL_SERVER);
            q.AddParameter("@cusip", cusip);
            q.AddParameter("@FromDate", startDate);
            q.AddParameter("@ToDate", endDate);
            q.AddParameter("@repoLine", repoLine);
            DataTable t = q.ExecuteTable();
            return t;
        }



        public static string GetTickerOrQueueIfNot(string server,string ticker_or_cusip)
        {
            if (String.IsNullOrEmpty(ticker_or_cusip))
                return "";
            ticker_or_cusip = ticker_or_cusip.Trim();
            ticker_or_cusip = ticker_or_cusip.Replace(" ", " ");
            string s = MT.GetTickerFromAsset(server, ticker_or_cusip, false);
            if (String.IsNullOrWhiteSpace(s))
            {
                UpdateDB.InsertUpdateBondToLoad(server, ticker_or_cusip);
                return "<NOT IN THE CAVE - QUEUED>";
            }
            else
                return ticker_or_cusip;
        }

        private static string GetRepoFacilityId(string server, string repoLine)
        {
            string sql = "SELECT  id FROM [HECM].[dbo].[RepoFacilities] WHERE name=@repoLine";
            Query q = new Query(sql, server);
            q.AddParameter("@repoLine", repoLine);
            return q.ExecuteSingle<string>();
        }

    }
}


--- FILE: Assets\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("Assets")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("Assets")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2013")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("0a9479f8-7a1c-4405-8635-7e5579847439")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: Assets\Trade.cs ---
namespace Assets
{
    public class Trade
    {
        public static double? AccruedInterestCPR(string ticker,double oface,DateTime buy_settle, DateTime settle_interested_in_accruing,double cpr)
        {
            if (!UtilsLib.Validate.IsValidInput(ticker))
                return null;
            if(buy_settle.SameMonth(settle_interested_in_accruing))
            {
                return AccruedInterest(ticker, oface, settle_interested_in_accruing);
            }
            
            
            
            
            double principal = System.Convert.ToDouble(Cashflows.ScheduledBalance(ticker, oface, buy_settle, cpr,settle_interested_in_accruing));
            double coupon = Cashflows.GetSingleCashflowNumber<double>("COUPON",ticker, oface, buy_settle,cpr,settle_interested_in_accruing);
            int days_accrued = BloombergLib.Bloomberg.GetInstance().GetData<int>(ticker, "DAYS_ACC", "SETTLE_DT=" + settle_interested_in_accruing.ToString("yyyMMdd"));
            
            double factor = principal / oface;
            

            if (factor == 0)
                factor = 1;

            double dollars = (oface * factor) * (coupon/100.0/360.0) * days_accrued;
            
           
            return dollars;
        }


        public static double? AccruedCpn(string ticker, DateTime settle_date)
        {
            
            if (!UtilsLib.Validate.IsValidInput(ticker))
                return null;

            double days_accrued = BloombergLib.Bloomberg.GetInstance()
                .GetData<double>(ticker, "DAYS_ACC", "SETTLE_DT=" + settle_date.ToString("yyyMMdd"));
            if (days_accrued == 0)
            {
                UtilsLib.Dates.XDateTime d = new UtilsLib.Dates.XDateTime(settle_date);
                d.AddBusinessDays(1);
                return AccruedCpn(ticker, d.Date);
            }

            double accrued = BloombergLib.Bloomberg.GetInstance()
                .GetData<double>(ticker, "INT_ACC", "SETTLE_DT=" + settle_date.ToString("yyyMMdd"));

            DateTime first_settle = BloombergLib.Bloomberg.GetInstance().GetData<DateTime>(ticker, "FIRST_SETTLE_DT");
            if (settle_date <= first_settle)
                return 0;

            double factor = BloombergLib.Bloomberg.GetInstance().GetData<double>(ticker, "MTG_FACTOR_SET_DT",
                "SETTLE_DT=" + settle_date.ToString("yyyMMdd"));
            
            double cface = 100;
            double cpn = ((accrued / days_accrued) / cface) * 360;
            
            return cpn;

        }

        public static double AccruedInterest(string ticker,double oface,DateTime settle_date)
        {
            double accrued = BloombergLib.Bloomberg.GetInstance().GetData<double>(ticker, "INT_ACC", "SETTLE_DT=" + settle_date.ToString("yyyMMdd"));
            double factor = BloombergLib.Bloomberg.GetInstance().GetData<double>(ticker, "MTG_FACTOR_SET_DT", "SETTLE_DT=" + settle_date.ToString("yyyMMdd"));
            if (factor == 0)
                factor = 1;
            double dollars = (oface * factor )/ 100.0 * accrued;
            return dollars;
        }
    }
}


--- FILE: Assets\UpdateDB.cs ---
namespace Assets
{
    public static class UpdateDB
    {
        public class UpdateDBHelper
        {
            public bool inserted;
            public string ticker;
        }
        public static UpdateDBHelper InsertIfNotExist(string server,string ticker,string bbg_id)
        {
            string sql = "exec InsertIfNotAvailable @ticker=@ticker,@bbg_id=@bbg_id,@final_ticker=@final_ticker|OUT OUTPUT,@created=@created|OUT OUTPUT";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker", ticker);
            q.AddParameter("@bbg_id", bbg_id);
            q.AddParameter("@final_ticker|OUT", new String(' ',30));
            q.AddParameter("@created|OUT", false);
            UpdateDBHelper u = new UpdateDBHelper();
            q.Execute();
            u.inserted = System.Convert.ToBoolean(q.Parameters["@created"]);
            u.ticker = System.Convert.ToString(q.Parameters["@final_ticker"]);
            return u;
        }

        public static void InsertUpdateBondToLoad(string server,string ticker_or_cusip)
        {
            string sql = "exec dbo.InsertBBGQueue @ticker_or_cusip=@ticker_or_cusip";
            Query q = new Query(sql, server);
            q.AddParameter("@ticker_or_cusip", ticker_or_cusip);
            q.Execute();
        }
    }
}


--- FILE: Assets\Utils.cs ---
namespace Assets
{
    public static class Utils
    {

        public static int CalcMTR(int age, int rate_reset_freq)
        {
            return rate_reset_freq - (age % rate_reset_freq);
        }

        
        
        
        
        
        
        

        
        
        
        
        

    }
}


--- FILE: MarketCloses\MarketCloses\Program.cs ---
namespace MarketCloses
{
    class Program
    {
        static void Main(string[] arg)
        {
            CommandLineArgs args = new CommandLineArgs(arg);
            string server = args["server"];
            bool mail = args.ContainsFlag("mail");
            string to = args["to"];
            string smtp_server = "";
            string vars = args.ContainsFlag("vars") ? args["vars"] : null;
            string cc = args.ContainsFlag("cc") ? args["cc"] : null;
            string bcc = args.ContainsFlag("bcc") ? args["bcc"] : null;
            string header_args = args.ContainsFlag("headers") ? args["headers"] : null;
            string tables = args.ContainsFlag("tables") ? args["tables"] : null;
            Mail.MailServerConfig mp = new Mail.MailServerConfig
            {
                server = args.ArgIfAvailableNotNull<string>("smtp_server"),
                user = args.ArgIfAvailableNotNull<string>("smtp_user"),
                pass = args.ArgIfAvailableNotNull<string>("smtp_pass"),
                port = args.ArgIfAvailableNotNull<int>("smtp_port", 25)
            };

            if (args.ContainsFlag("mailprofile"))
            {
                mp = UtilsLib.Mail.MailProfiles.GetProfiles()[args["mailprofile"]];
            }


            Nullable<int> load_id = null;
            if (args.ContainsFlag("load_id"))
                load_id = System.Convert.ToInt32(args["load_id"]);

 

            MarketClosesLib.MCHelper mch = new MarketClosesLib.MCHelper(server, Console.WriteLine);
            mch.LoadConfig(load_id);
            mch.GetAndSaveCloses();
            mch.DoPostAction();

            if(mail)
            {
                Mail m = new Mail(mp);
                Console.WriteLine($"Sending Mail: {String.Join(",", to)} / CC: {String.Join(",", cc)} / BCC: {String.Join(",", bcc)} ");

                List<IFormatHelper> fh = Database.RRHelper.GetFormats(server);
    
                DataTable tbl = GetSummary(server, load_id);
                HTMLUtils.HTMLHelper hh = UtilsLib.HTMLUtils.QuickToHtml(tbl, vars, header_args, tables, fh);
                string subject = "[" + mch.record_written + "] Rate Closes Written";
                if(mch.warnings.Count > 0)
                {
                    subject = "[WARNING] - " + subject;
                }


                m.SendMail(to, cc, bcc, "Market Closes", hh.html, null);
                
            }
          
        }

        public static DataTable GetSummary(string server,Nullable<int> load_id)
        {
            Query q = new Query("DoDSummary.sql", server);
            q.AddParameter("@load_id", load_id);
            return q.ExecuteTable();
        }

       
        
    }
}


--- FILE: MarketCloses\MarketCloses\Properties\AssemblyInfo.cs ---
[assembly: AssemblyTitle("MarketCloses")]
[assembly: AssemblyDescription("")]
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Microsoft")]
[assembly: AssemblyProduct("MarketCloses")]
[assembly: AssemblyCopyright("Copyright © Microsoft 2017")]
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]




[assembly: ComVisible(false)]


[assembly: Guid("5164fcf5-db52-4f68-8a39-83633079c3c9")]











[assembly: AssemblyVersion("1.0.0.0")]
[assembly: AssemblyFileVersion("1.0.0.0")]


--- FILE: MarketCloses\MarketCloses\SQL\DoDSummary.sql ---
declare @asOf date
select @asOf = dbo.AddBdays(dbo.Today(),-1)

select distinct t.asOf,t.ticker,t.rate [today],p.rate [prior],t.rate-p.rate [delta] 
  from 
    MarketCloses t
    left join MarketCloses p on p.ticker = t.ticker and p.asOf = dbo.AddBdays(@asOf, -1)
	  left join MarketCloseConfig mcc on mcc.load_id = @load_id
    where 
      t.asOf = @asOf
