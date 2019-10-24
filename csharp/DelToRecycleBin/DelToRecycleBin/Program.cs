using Microsoft.VisualBasic.FileIO;//记得"Add References"并选择"Microsoft.VisualBasic".

namespace DelToRecycleBin
{
    class Program
    {
        static int Main(string[] args)
        {
            int retVal = 0;
            try
            {
                do
                {
                    if (args.Length == 0)
                    {
                        retVal = 0;
                        break;
                    }
                    string path = args[0];
                    if (System.IO.Directory.Exists(path))
                    {
                        Microsoft.VisualBasic.FileIO.FileSystem.DeleteDirectory(path, UIOption.OnlyErrorDialogs, RecycleOption.SendToRecycleBin);
                    }
                    else if (System.IO.File.Exists(path))
                    {
                        Microsoft.VisualBasic.FileIO.FileSystem.DeleteFile(path, UIOption.OnlyErrorDialogs, RecycleOption.SendToRecycleBin);
                    }
                    else
                    {
                        retVal = 1;
                        string errMsg = string.Format("既不是文件,也不是目录,无法处理,path={0}", path);
                        System.Console.Error.WriteLine(errMsg);
                    }
                } while (false);
            }
            catch (System.Exception ex)
            {
                retVal = -1;
                System.Console.Error.WriteLine(ex);
            }
            return retVal;
        }
    }
}
