using Microsoft.AspNetCore.Localization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace McpServer
{
    public class DataIO
    {
        private const string OutputDir = "Results";
        private const string IntermediateOutputName = "IntermidiateResult.csv";
        private const string FinalResultOutputName = "FinalResult_{0}.csv";
        private int _outputIndex = 0;
        public bool ReadData(string dir, out double[] x, out double[] y)
        {
            x = new double[] { };
            y = new double[] { };
            
            string file = string.Empty;
            if (File.Exists(dir))
            {
                file = dir;
            }
            else
            {
                var files = Directory.GetFiles(dir);
                if (files.Length == 0)
                {
                    return false;
                }
                file = files[0];
            }
            var xList = new List<double>();
            var yList = new List<double>();
            using(var sr = new StreamReader(file))
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
        public bool WriteData(IList<double> x, IList<double> y, out string path)
        {
            path = Path.Combine(Directory.GetCurrentDirectory(), OutputDir, IntermediateOutputName);
            using(var sw = new StreamWriter(path, false, Encoding.Default))
            {
                for (int i = 0; i < x.Count; i++)
                {
                    sw.Write($"{x[i]}, {y[i]}");
                    sw.WriteLine();
                }
            }
            return true;
        }
        public bool WriteVisualizationData(IList<double> x, List<IList<double>> ys, List<string> columnHeaders, out string path)
        {
            path = Path.Combine(Directory.GetCurrentDirectory(), OutputDir, string.Format(FinalResultOutputName, _outputIndex++));
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
