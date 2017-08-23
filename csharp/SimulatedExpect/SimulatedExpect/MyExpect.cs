using System.Collections.Generic;
using System.Linq;

namespace SimulatedExpect
{
    class MyExpect : System.IDisposable
    {
        public void Dispose()
        {
            if (this.m_childProcess != null)
            {
                this.m_childProcess.Dispose();
                this.m_childProcess = null;
            }
        }

        public void run(string path, System.Text.Encoding encoding)
        {
            string content = System.IO.File.ReadAllText(path, encoding);
            //使用开源的类库"Newtonsoft.Json"(下载地址http://json.codeplex.com/). 下载后加入工程就能用.
            //CodePlex是微软于2006年推出的开源软件托管平台, 将于2017年12月关闭, 届时会将代码迁移到github上.
            var jArrObj = (Newtonsoft.Json.Linq.JArray)Newtonsoft.Json.JsonConvert.DeserializeObject(content);
            do_jarray(jArrObj);

            return;
        }

        private void do_spawn(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            var allOpt = (Newtonsoft.Json.Linq.JObject)cmdLine[this.spawn];
            //
            string filePath = null;
            string arguments = null;
            string workingDirectory = null;

            Newtonsoft.Json.Linq.JToken tokenValue = null;
            if (allOpt.TryGetValue("file", out tokenValue))
            {
                filePath = (tokenValue as Newtonsoft.Json.Linq.JValue).Value as string;
            }
            if (allOpt.TryGetValue("args", out tokenValue))
            {
                arguments = (tokenValue as Newtonsoft.Json.Linq.JValue).Value as string;
            }
            if (allOpt.TryGetValue("workdir", out tokenValue))
            {
                workingDirectory = (tokenValue as Newtonsoft.Json.Linq.JValue).Value as string;
            }

            createChildProcess(filePath, arguments, workingDirectory);
            //
            return;
        }

        private void do_expect(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            var allAction = (Newtonsoft.Json.Linq.JObject)cmdLine[this.expect];

            //在所有的要搜索的字符串中,可能包含指代程序退出(EOF)的空字符串(""),要把它过滤掉.
            var allSearchData = allAction.Properties().Select(item => item.Name.ToString()).Where(item => 0 < item.Length).ToArray();

            //每一次读取屏幕输出之前,都设置一下超时时间.
            if (m_dict.ContainsKey(this.timeout))
            {
                int timeoutSeconds = System.Convert.ToInt32(m_dict[this.timeout]);
                m_childProcess.Options.TimeoutMilliseconds = timeoutSeconds * 1000;
            }

            bool enableRegexp = true;
            if (m_dict.ContainsKey(this.regexp))
            {
                int regexpFlag = System.Convert.ToInt32(m_dict[this.regexp]);
                enableRegexp = regexpFlag == 0 ? false : true;
            }

            bool isExit = false;
            bool isTimeout = false;
            string selectedData = null;
            m_childProcess.ReadZx(allSearchData, enableRegexp, ref selectedData, ref isExit, ref isTimeout);

            Newtonsoft.Json.Linq.JArray jArrObj = null;
            if (isExit)
            {
                Newtonsoft.Json.Linq.JToken tokenValue = null;
                if (allAction.TryGetValue(this.EOF, out tokenValue))
                {
                    jArrObj = (Newtonsoft.Json.Linq.JArray)tokenValue;
                }
                else
                {
                    string message = string.Format("isExit=true,{0}", cmdLine.ToString());
                    throw new System.Exception(message);
                }
            }
            else
            {
                if (isTimeout)
                {
                    jArrObj = null;
                }
                else
                {
                    jArrObj = (Newtonsoft.Json.Linq.JArray)allAction[selectedData];
                }
            }

            if (jArrObj != null)
            {
                do_jarray(jArrObj);
            }

            return;
        }

        private void do_set(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            var allPair = cmdLine[this.set] as Newtonsoft.Json.Linq.JObject;
            System.Diagnostics.Trace.Assert(allPair != null, cmdLine.ToString());
            //
            foreach (var pair in allPair)
            {
                var obj = allPair[pair.Key] as Newtonsoft.Json.Linq.JValue;
                string value = obj.Value.ToString();

                if (this.m_dict.ContainsKey(pair.Key))
                    this.m_dict[pair.Key] = value;
                else
                    this.m_dict.Add(pair.Key, value);
            }
            //
            return;
        }

        private void do_sleep(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            //C# 提供 is 和 as 运算符，使你可以在实际执行强制转换之前测试兼容性。
            var jValue = (cmdLine[this.sleep] as Newtonsoft.Json.Linq.JValue);
            int seconds = System.Convert.ToInt32(jValue.Value);
            System.Diagnostics.Trace.Assert(0 < seconds, cmdLine.ToString());
            //
            System.Threading.Thread.Sleep(seconds * 1000);
            //
            return;
        }

        private void do_send(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            var jValue = (cmdLine[this.send] as Newtonsoft.Json.Linq.JValue);
            string data = (jValue.Value as string);
            System.Diagnostics.Trace.Assert(data != null, cmdLine.ToString());
            //
            m_childProcess.Write(data);
            //
            return;
        }

        private void do_send_user(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            var jValue = (cmdLine[this.send_user] as Newtonsoft.Json.Linq.JValue);
            string data = (jValue.Value as string);
            System.Diagnostics.Trace.Assert(data != null, cmdLine.ToString());
            //
            System.Console.Write(data);
            //
            return;
        }

        private void do_debug(Newtonsoft.Json.Linq.JObject cmdLine)
        {
            var jValue = (cmdLine[this.debug] as Newtonsoft.Json.Linq.JValue);
            string data = (jValue.Value as string);
            System.Diagnostics.Trace.Assert(data != null, cmdLine.ToString());
            //
            if /**/ (data == "latest_output")
            {
                System.Console.WriteLine(m_childProcess.LatestConsoleOutput);
            }
            else if (data == "total_output")
            {
                System.Console.WriteLine(m_childProcess.TotalConsoleOutput);
            }
            else if (data == "exit_code")
            {
                if (m_childProcess.HasChildExited)
                {
                    string message = string.Format("exit_code=[{0}]", m_childProcess.ChildExitCode);
                    System.Console.WriteLine(message);
                }
                else
                {
                    string message = string.Format("exit_code=[{0}]", "the program has not yet quit");
                    System.Console.WriteLine(message);
                }
            }
            else if (data == "local_time")
            {
                string message = string.Format("local_time=[{0}]", System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));
                System.Console.WriteLine(message);
            }
            else
            {
                System.Diagnostics.Trace.Assert(false, cmdLine.ToString());
            }
            //
            return;
        }

        private void do_jarray(Newtonsoft.Json.Linq.JArray jArrObj)
        {
            foreach (var tokenValue in jArrObj)
            {
                var cmdLine = tokenValue as Newtonsoft.Json.Linq.JObject;

                var cmdKeyArr = cmdLine.Properties().Select(item => item.Name.ToString()).ToArray();
                System.Diagnostics.Trace.Assert(1 == cmdKeyArr.Length && 0 < cmdKeyArr[0].Length);
                string cmdKey = cmdKeyArr[0];

                if /**/ (cmdKey == this.spawn)
                    do_spawn(cmdLine);
                else if (cmdKey == this.expect)
                    do_expect(cmdLine);
                else if (cmdKey == this.set)
                    do_set(cmdLine);
                else if (cmdKey == this.sleep)
                    do_sleep(cmdLine);
                else if (cmdKey == this.send)
                    do_send(cmdLine);
                else if (cmdKey == this.send_user)
                    do_send_user(cmdLine);
                else if (cmdKey == this.debug)
                    do_debug(cmdLine);
                else
                    System.Diagnostics.Trace.Assert(false);
            }

            return;
        }

        private void createChildProcess(string filePath, string arguments, string workingDirectory)
        {
            System.Diagnostics.Trace.Assert(m_childProcess == null);

            if /**/ (filePath != null && arguments == null && workingDirectory == null)
                m_childProcess = new Cbonnell.DotNetExpect.ChildProcess(filePath);
            else if (filePath != null && arguments != null && workingDirectory == null)
                m_childProcess = new Cbonnell.DotNetExpect.ChildProcess(filePath, arguments);
            else if (filePath != null && arguments != null && workingDirectory != null)
                m_childProcess = new Cbonnell.DotNetExpect.ChildProcess(filePath, arguments, workingDirectory);
            else
                System.Diagnostics.Trace.Assert(false);
        }

        private Cbonnell.DotNetExpect.ChildProcess m_childProcess = null;
        private Dictionary<string, string> m_dict = new System.Collections.Generic.Dictionary<string, string>();
        private readonly string spawn = "spawn";
        private readonly string expect = "expect";
        private readonly string set = "set";
        private readonly string send = "send";
        private readonly string send_user = "send_user";
        private readonly string sleep = "sleep";
        private readonly string debug = "debug";
        private readonly string EOF = ""; // 用空字符串代替linux的expect中的EOF标志.
        private readonly string timeout = "timeout";
        private readonly string regexp = "regexp";
    };
}
