using MathNet.Numerics;
using ModelContextProtocol.Server;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace McpServer
{
    [McpServerToolType]
    public sealed class McpTools
    {
        [McpServerTool, Description("Perform a MCP server test by returning hello world")]
        public static string DoHelloWorldTest()
        {
            var res = "Hello world from MCP server!";
            Console.WriteLine(res);
            return res;
        }
        [McpServerTool, Description("Test temp file directory by returning the temp file directory passed in function argument")]
        public static string EchoTempDir([Description("Temp file directory")] string tempFileDir)
        {
            return tempFileDir;
        }
        [McpServerTool, Description("Read data from uploaded file, apply savitzky-golay filter to smooth the data, and returns the path where the smoothed data is saved")]
        public static string SavitzkyGolayFilter(
            DataIO ioCtrl,
            [Description("Uploaded file directory where the uploaded file is")] string uploadedFileDir,
            [Description("Filter's window size, larger means more smoothing effect. Must be between 11 and 101, and must be an odd number. Window size of 31 is a good starting point")] int windowSize,
            [Description("Filter's polynomial order, should be between 3 and 5. 3 is a good starting point")] int polynomialOrder = 3)
        {
            if (windowSize % 2 == 0)
            {
                throw new ArgumentException("Window size must be odd.");
            }
            if (polynomialOrder >= windowSize)
            {
                throw new ArgumentException("polynomialOrder can not over windowSize");
            }
            if (!ioCtrl.ReadData(uploadedFileDir, out var x, out var y))
            {
                throw new ArgumentException("Failed to read data file");
            }
            List<double> result = y.ToList();
            int halfwidth = windowSize / 2;
            for (int i = halfwidth; i < result.Count - halfwidth; i++)
            {
                List<double> index = new List<double>();
                List<double> values = new List<double>();
                for (int k = -halfwidth; k <= halfwidth; k++)
                {
                    index.Add(i + k);
                    values.Add(result[i + k]);
                }
                double[] c = Fit.Polynomial(index.ToArray(), values.ToArray(), polynomialOrder);
                double newvaleu = Polynomial.Evaluate(i, c);
                result[i] = newvaleu;
            }
            var resultPath = Path.Combine(Directory.GetCurrentDirectory(), "result_smooth.csv");
            if (!ioCtrl.WriteData(resultPath, x, new List<IList<double>>() { y, result }, new List<string>() { "Original Data", "Smoothed Data" }))
            {
                throw new ArgumentException("Failed to write result file");
            }
            return resultPath;
        }
        [McpServerTool, Description("Read data from uploaded file, use AirPLS algorithm to remove baseline, and returns the path where the processed data is saved")]
        public static string AirPLS(
            DataIO ioCtrl,
            [Description("Uploaded file directory where the uploaded file is")] string uploadedFileDir,
            [Description("Lambda of the AirPLS algorithm. Should be between 50 and 150, and default value should be 100. " +
            "When lambda is increased, the result baseline becomes smoother, preserving features in the original data while leaving some baseline behind. " +
            "When lambda is decreased, the result baseline becomes closer to the original data. The algorithm will remove more baseline in exchange of a higher possibility of removing useful features in the original data")]double lambda = 100, 
            [Description("Number of iterations in algorithm. Should be kept as 20 unless the user specifically ask to change this value")]int itermax = 20)
        {
            if (!ioCtrl.ReadData(uploadedFileDir, out var x, out var origSig))
            {
                throw new ArgumentException("Failed to read data file");
            }
            double[] corrected = new double[origSig.Count()];
            double[] baseline = new double[origSig.Count()];
            AirPLS_AMPD.airPLS(origSig, corrected, baseline, origSig.Count(), lambda, itermax);
            var resultPath = Path.Combine(Directory.GetCurrentDirectory(), "result_baseline.csv");
            if (!ioCtrl.WriteData(resultPath, x, new List<IList<double>>() { origSig, corrected, baseline }, new List<string>() { "Original Data", "Data(no baseline)", "baseline" }))
            {
                throw new ArgumentException("Failed to write result file");
            }
            return resultPath;
        }
    }
}
