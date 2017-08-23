namespace SimulatedExpect
{
    class Program
    {
        static int Main(string[] args)
        {
            int retVal = 0;

            for (int i = 0; true && i < args.Length; ++i)//前期调试.
            {
                System.Console.WriteLine(string.Format("args[{0}]=[{1}]", i, args[i]));
            }

            string path = "config.json";
            if (0 < args.Length)
            {
                path = args[0];
            }
            System.Text.Encoding encoding = System.Text.Encoding.UTF8;

            try
            {
                using (MyExpect expect = new MyExpect())
                {// using语句定义了一个范围, 在范围结束时, 就自动调用这个类的实例的Dispose函数.
                    expect.run(path, encoding);
                }
            }
            catch (System.Exception ex)
            {
                System.Console.WriteLine(ex);
                retVal = 1;
            }

            return retVal;
        }
    }
}
