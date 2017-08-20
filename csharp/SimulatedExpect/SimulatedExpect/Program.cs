namespace SimulatedExpect
{
    class Program
    {
        static void Main(string[] args)
        {
            System.Text.Encoding encoding = System.Text.Encoding.UTF8;

            string path = "config.json";
            if (2 <= args.Length)
                path = args[1];

            //using语句, 定义一个范围, 在范围结束时处理对象.
            //只要离开了这个代码段, 就自动调用这个类实例的Dispose函数.
            using (MyExpect expect = new MyExpect())
            {
                expect.run(path, encoding);
            }

            return;
        }
    }
}
