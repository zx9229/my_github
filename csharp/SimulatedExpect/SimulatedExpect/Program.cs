namespace SimulatedExpect
{
    class Program
    {
        static void Main(string[] args)
        {
            for (int i = 0; true && i < args.Length; ++i)//前期调试.
            {
                System.Console.WriteLine(string.Format("args[{0}]=[{1}]", i, args[i]));
            }

            string path = "config.json";
            if (1 <= args.Length)
            {
                path = args[0];
            }
            System.Text.Encoding encoding = System.Text.Encoding.UTF8;

            try
            {
                //using语句定义了一个范围, 在范围结束时, 就自动调用这个类的实例的Dispose函数.
                using (MyExpect expect = new MyExpect())
                {
                    expect.run(path, encoding);
                }
            }
            catch (System.Exception ex)
            {
                System.Console.WriteLine(ex);
            }

            return;
        }
    }
}
