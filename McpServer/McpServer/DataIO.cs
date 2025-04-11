using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace McpServer
{
    public class DataIO
    {
        public bool ReadData(string dir, out double[] x, out double[] y)
        {
            x = new double[] { };
            y = new double[] { };
            var files = Directory.GetFiles(dir);
            if(files.Length == 0)
            {
                return false;
            }
            var xList = new List<double>();
            var yList = new List<double>();
            using(var sr = new StreamReader(files[0]))
            {
                while(!sr.EndOfStream)
                {
                    var line = sr.ReadLine()?.Split(',').Select(double.Parse);
                    if(line == null)
                    {
                        continue;
                    }
                    xList.Add(line.ElementAt(0));
                    yList.Add(line.ElementAt(1));
                }
            }
            x = xList.ToArray();
            y = yList.ToArray();
            return true;
        }
        public bool WriteData(string path, IList<double> x, List<IList<double>> ys, List<string> columnHeaders)
        {
            using(var sw = new StreamWriter(path, false, Encoding.Default))
            {
                sw.Write("X");
                foreach(var item in columnHeaders)
                {
                    sw.Write($", {item}");
                }
                sw.WriteLine();
                for(int i = 0; i < x.Count; i++)
                {
                    sw.Write($"{x[i]}");
                    foreach(var item in ys)
                    {
                        sw.Write($", {item[i]}");
                    }
                    sw.WriteLine();
                }
            }
            return true;
        }
    }
}
