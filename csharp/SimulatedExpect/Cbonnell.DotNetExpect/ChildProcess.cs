﻿/*
DotNetExpect
Copyright (c) Corey Bonnell, All rights reserved.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 3.0 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library. */

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace Cbonnell.DotNetExpect
{
    /// <summary>
    /// Represents a child process whose console input and output can be accessed.
    /// </summary>
    public class ChildProcess : IDisposable
    {
        private ProxyProcessManager proxy = new ProxyProcessManager();
        private string  totalConsoleOutput = "";//读出来的全部的控制台输出.
        private string latestConsoleOutput = "";//读出来的最新的控制台输出.

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="filePath">The path to the child process. The semantics in terms of how relative paths are handled are the same as <see cref="System.Diagnostics.ProcessStartInfo.FileName"/> with <see cref="System.Diagnostics.ProcessStartInfo.UseShellExecute"/> set to <b>false</b>.</param>
        public ChildProcess(string filePath) : this(filePath, String.Empty) { }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="filePath">The path to the child process. The semantics in terms of how relative paths are handled are the same as <see cref="System.Diagnostics.ProcessStartInfo.FileName"/> with <see cref="System.Diagnostics.ProcessStartInfo.UseShellExecute"/> set to <b>false</b>.</param>
        /// <param name="options">The <see cref="ChildProcessOptions"/> to use when accessing the console input and output of the child process.</param>
        public ChildProcess(string filePath, ChildProcessOptions options) : this(filePath, String.Empty, options) { }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="filePath">The path to the child process. The semantics in terms of how relative paths are handled are the same as <see cref="System.Diagnostics.ProcessStartInfo.FileName"/> with <see cref="System.Diagnostics.ProcessStartInfo.UseShellExecute"/> set to <b>false</b>.</param>
        /// <param name="arguments">The command line arguments for the child process.</param>
        public ChildProcess(string filePath, string arguments) : this(filePath, arguments, Environment.CurrentDirectory) { }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="filePath">The path to the child process. The semantics in terms of how relative paths are handled are the same as <see cref="System.Diagnostics.ProcessStartInfo.FileName"/> with <see cref="System.Diagnostics.ProcessStartInfo.UseShellExecute"/> set to <b>false</b>.</param>
        /// <param name="arguments">The command line arguments for the child process.</param>
        /// <param name="options">The <see cref="ChildProcessOptions"/> to use when accessing the console input and output of the child process.</param>
        public ChildProcess(string filePath, string arguments, ChildProcessOptions options) : this(filePath, arguments, Environment.CurrentDirectory, options) { }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="filePath">The path to the child process. The semantics in terms of how relative paths are handled are the same as <see cref="System.Diagnostics.ProcessStartInfo.FileName"/> with <see cref="System.Diagnostics.ProcessStartInfo.UseShellExecute"/> set to <b>false</b>.</param>
        /// <param name="arguments">The command line arguments for the child process.</param>
        /// <param name="workingDirectory">The working directory for the child process.</param>
        public ChildProcess(string filePath, string arguments, string workingDirectory) : this(filePath, arguments, workingDirectory, new ChildProcessOptions()) { }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="filePath">The path to the child process. The semantics in terms of how relative paths are handled are the same as <see cref="System.Diagnostics.ProcessStartInfo.FileName"/> with <see cref="System.Diagnostics.ProcessStartInfo.UseShellExecute"/> set to <b>false</b>.</param>
        /// <param name="arguments">The command line arguments for the child process.</param>
        /// <param name="workingDirectory">The working directory for the child process.</param>
        /// <param name="options">The <see cref="ChildProcessOptions"/> to use when accessing the console input and output of the child process.</param>
        public ChildProcess(string filePath, string arguments, string workingDirectory, ChildProcessOptions options)
        {
            if (filePath == null)
            {
                throw new ArgumentNullException("filePath");
            }
            if (arguments == null)
            {
                throw new ArgumentNullException("arguments");
            }
            if (workingDirectory == null)
            {
                throw new ArgumentNullException("workingDirectory");
            }
            if (options == null)
            {
                throw new ArgumentNullException("options");
            }

            this.Options = options;

            try
            {
                this.proxy.Start();
                this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.StartProcess);
                this.proxy.CommandPipeWriter.Write(filePath);
                this.proxy.CommandPipeWriter.Write(arguments);
                this.proxy.CommandPipeWriter.Write(workingDirectory);
                this.proxy.CommandPipeWriter.Flush();

                this.readResponseAndThrow();
            }
            catch (Exception)
            {
                this.Dispose();
                throw;
            }
        }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="pid">The process ID of the console process.</param>
        /// <remarks>This constructor is used to manipulate console I/O for a process that is already running.</remarks>
        public ChildProcess(int pid) : this(pid, new ChildProcessOptions()) { }

        /// <summary>
        /// Creates a new instance of <see cref="ChildProcess"/>.
        /// </summary>
        /// <param name="pid">The process ID of the console process.</param>
        /// <param name="options">The <see cref="ChildProcessOptions"/> to use when accessing the console input and output of the child process.</param>
        /// <remarks>This constructor is used to manipulate console I/O for a process that is already running.</remarks>
        public ChildProcess(int pid, ChildProcessOptions options)
        {
            if (options == null)
            {
                throw new ArgumentNullException("options");
            }

            this.Options = options;

            try
            {
                this.proxy.Start();
                this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.SetPid);
                this.proxy.CommandPipeWriter.Write(pid);
                this.proxy.CommandPipeWriter.Flush();

                this.readResponseAndThrow();
            }
            catch (Exception)
            {
                this.Dispose();
                throw;
            }
        }

        /// <summary>
        /// Reads the child process's console output (screen buffer) until the content of the screen output matches the specified <see cref="Regex"/>.
        /// </summary>
        /// <param name="regex">The regular expression to match the console screen output against.</param>
        /// <returns>A <see cref="Match"/> that was returned after matching the console output with the specified <see cref="Regex"/>.</returns>
        public Match Match(Regex regex)
        {
            if (regex == null)
            {
                throw new ArgumentNullException("regex");
            }

            this.checkDisposedAndThrow();

            return this.readLoopWithTimeout<Match>((s) => regex.Match(s), (m) => m.Success, this.Options.TimeoutMilliseconds);
        }

        /// <summary>
        /// Reads the child process's console output (screen buffer) until the content of the screen output contains the expected data.
        /// </summary>
        /// <param name="expectedData">The string for which to search.</param>
        /// <returns>The console output.</returns>
        public string Read(string expectedData)
        {
            if (expectedData == null)
            {
                throw new ArgumentNullException("expectedData");
            }

            this.checkDisposedAndThrow();

            return this.readLoopWithTimeout<string>((s) => s, (s) => s.Contains(expectedData), this.Options.TimeoutMilliseconds);
        }

        /// <summary>
        /// Reads the child process's console output (screen buffer) until the content of the screen output contains the expected data.
        /// </summary>
        /// <param name="allData">要搜索的所有字符串.</param>
        /// <param name="enableRegexp">是否以正则表达式的方式搜索字符串.</param>
        /// <param name="selectedData">找到的第一个字符串.</param>
        /// <param name="isExit">子进程是否已经退出.</param>
        /// <param name="isTimeout">搜索超时.</param>
        /// <returns>The console output.</returns>
        public string ReadZx(IEnumerable<string> allData, bool enableRegexp, ref string selectedData, ref bool isExit, ref bool isTimeout)
        {
            return readLoopWithTimeoutZx(allData, ref selectedData, enableRegexp, this.Options.TimeoutMilliseconds, ref isExit, ref isTimeout);
        }

        /// <summary>
        /// Writes the specified string to the child process's console.
        /// </summary>
        /// <param name="data">The string data to write to the child process's console.</param>
        public void Write(string data)
        {
            if (data == null)
            {
                throw new ArgumentNullException("data");
            }

            this.checkDisposedAndThrow();

            if (this.Options.AttachConsole)
            {
                this.attachConsole();
            }

            this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.WriteConsole);
            this.proxy.CommandPipeWriter.Write(data);
            this.proxy.CommandPipeWriter.Flush();
            this.readResponseAndThrow();
        }

        /// <summary>
        /// Writes the specified string to the child process's console, first appending the value of <see cref="ChildProcessOptions.NewLine"/> to the string.
        /// </summary>
        /// <param name="data">The string data to write to the child process's console.</param>
        public void WriteLine(string data)
        {
            if (data == null)
            {
                throw new ArgumentNullException("data");
            }

            data += this.Options.NewLine;

            this.Write(data);
        }

        /// <summary>
        /// Kills the child process.
        /// </summary>
        /// <returns>The exit code of the killed child process.</returns>
        /// <remarks>After this method is called, this object is disposed no further operations can be performed on this object.</remarks>
        public int Kill()
        {
            this.checkDisposedAndThrow();

            this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.KillProcess);
            this.proxy.CommandPipeWriter.Flush();
            this.readResponseAndThrow();
            int exitCode = this.proxy.CommandPipeReader.ReadInt32(); // read the exit code

            this.Dispose();

            return exitCode;
        }

        /// <summary>
        /// Clears the child process's console output.
        /// </summary>
        public void ClearConsole()
        {
            this.checkDisposedAndThrow();

            this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.ClearConsole);
            this.proxy.CommandPipeWriter.Flush();
            this.readResponseAndThrow();
        }

        /// <summary>
        /// Retrieves the process ID of the spawned child process.
        /// </summary>
        public int ChildProcessId
        {
            get
            {
                this.checkDisposedAndThrow();

                this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.GetPid);
                this.proxy.CommandPipeWriter.Flush();
                this.readResponseAndThrow();

                return this.proxy.CommandPipeReader.ReadInt32();
            }
        }

        /// <summary>
        /// Retrieves the exit code of a child process that has exited (stopped executing).
        /// </summary>
        public int ChildExitCode
        {
            get
            {
                this.checkDisposedAndThrow();

                this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.GetProcessExitCode);
                this.proxy.CommandPipeWriter.Flush();
                this.readResponseAndThrow();

                return this.proxy.CommandPipeReader.ReadInt32();
            }
        }

        /// <summary>
        /// Retrieves whether or not a child process has exited (stopped executing).
        /// </summary>
        public bool HasChildExited
        {
            get
            {
                this.checkDisposedAndThrow();

                this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.GetHasProcessExited);
                this.proxy.CommandPipeWriter.Flush();
                this.readResponseAndThrow();

                return this.proxy.CommandPipeReader.ReadBoolean();
            }
        }

        /// <summary>
        /// Retrieves the <see cref="ChildProcessOptions"/> used by the current instance of <see cref="ChildProcess"/>.
        /// </summary>
        public ChildProcessOptions Options
        {
            get;
            private set;
        }

        /// <summary>
        /// 读出来的全部的控制台输出.
        /// </summary>
        public string TotalConsoleOutput
        {
            get
            {
                return this.totalConsoleOutput;
            }
        }

        /// <summary>
        /// 读出来的最新的控制台输出.
        /// </summary>
        public string LatestConsoleOutput
        {
            get
            {
                return this.latestConsoleOutput;
            }
        }

        /// <summary>
        /// Disposes the current instance of <see cref="ChildProcess"/>.
        /// </summary>
        public void Dispose()
        {
            if (this.proxy != null)
            {
                this.proxy.Dispose();
                this.proxy = null;
            }

            this.totalConsoleOutput = "";
            this.latestConsoleOutput = "";
        }

        private void checkDisposedAndThrow()
        {
            if (this.proxy == null)
            {
                throw new ObjectDisposedException(this.GetType().FullName);
            }
        }

        private TReturn readLoopWithTimeout<TReturn>(Converter<string, TReturn> string2TypeConverter, Predicate<TReturn> isCompleteDelegate, int timeoutMilliseconds)
        {
            TimeSpan timeoutSpan = timeoutMilliseconds >= 0 ? TimeSpan.FromMilliseconds(timeoutMilliseconds) : default(TimeSpan);

            DateTime startTime = DateTime.Now;
            TReturn returnValue = default(TReturn);
            while (timeoutMilliseconds < 0 || DateTime.Now < startTime + timeoutSpan)
            {
                string output = this.readConsoleOutput();
                returnValue = string2TypeConverter.Invoke(output);
                if (isCompleteDelegate.Invoke(returnValue))
                {
                    break;
                }

                // if we're here, then default the return value and loop back because it doesn't satisfy our condition
                returnValue = default(TReturn);
            }

            // if we're here then we've either satisified the condition or we timed out
            // compare the return value to the default for the return type to determine if we timed out or not
            if (Object.Equals(returnValue, default(TReturn)))
            {
                throw new TimeoutException();
            }

            if (this.Options.ClearConsole)
            {
                this.ClearConsole();
            }

            return returnValue;
        }

        private string readLoopWithTimeoutZx(IEnumerable<string> allData, ref string selectedData, bool isRegex, int timeoutMilliseconds, ref bool isExit, ref bool isTimeout)
        {
            string output = null;

            selectedData = null;
            isExit = false;
            isTimeout = false;

            TimeSpan timeoutSpan = timeoutMilliseconds >= 0 ? TimeSpan.FromMilliseconds(timeoutMilliseconds) : default(TimeSpan);

            for (DateTime startTime = DateTime.Now; ;)
            {
                if (0 <= timeoutMilliseconds && startTime + timeoutSpan <= DateTime.Now)
                {
                    isTimeout = true;
                    break;
                }

                if (this.HasChildExited)
                {
                    isExit = true;
                    break;
                }

                output = this.readConsoleOutput();

                if (isRegex)
                {
                    selectedData = allData.FirstOrDefault(item => System.Text.RegularExpressions.Regex.IsMatch(output, item));
                }
                else
                {
                    selectedData = allData.FirstOrDefault(item => output.Contains(item));
                }

                if (selectedData != null)
                {
                    break;
                }
            }

            if (!isExit && !isTimeout && this.Options.ClearConsole)
            {
                this.totalConsoleOutput += output;
                this.ClearConsole();
            }

            return output;
        }

        private string readConsoleOutput()
        {
            if (this.Options.AttachConsole)
            {
                this.attachConsole();
            }

            this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.ReadConsole);
            this.proxy.CommandPipeWriter.Flush();
            this.readResponseAndThrow();

            this.latestConsoleOutput = this.proxy.CommandPipeReader.ReadString();

            return this.latestConsoleOutput;
        }

        private void attachConsole()
        {
            if (this.HasChildExited)
            {
                string message = string.Format("can not attachConsole, ChildExitCode={0}", this.ChildExitCode);
                throw new Exception(message);
            }

            this.proxy.CommandPipeWriter.Write((byte)ProxyCommand.AttachConsole);
            this.proxy.CommandPipeWriter.Write(this.Options.AttachConsoleTimeoutMilliseconds);
            this.proxy.CommandPipeWriter.Flush();
            this.readResponseAndThrow();
        }

        private void readResponseAndThrow()
        {
            CommandResult result = (CommandResult)this.proxy.CommandPipeReader.ReadByte();
            if (result != CommandResult.Success)
            {
                throw new OperationFailedException(result);
            }
        }
    }
}
