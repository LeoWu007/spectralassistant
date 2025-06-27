using MathNet.Numerics;
using Microsoft.Extensions.AI;
using ModelContextProtocol.Server;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RamanAnalyzeModel;
using RamanAnalyzeModel.Model;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace McpServer
{
    [McpServerToolType]
    public sealed class AlgorithmTools
    {
        [McpServerTool, Description("Read data from uploaded file, apply savitzky-golay filter to smooth the data, and returns the path where the smoothed data is saved")]
        public static string SavitzkyGolayFilter(
            DataIO ioCtrl,
            [Description("Uploaded file directory where the uploaded file is")] string uploadedFileDir,
            [Description("Filter's window size, larger means more smoothing effect. Must be between 11 and 101, and must be an odd number. Window size of 31 is a good starting point")] int windowSize,
            [Description("Filter's polynomial order, should be between 3 and 5. 3 is a good starting point")] int polynomialOrder = 3)
        {
            var toolRes = new ToolExecutionResult() { VisualizationType = VisualizationType.LineChart };
            if (windowSize % 2 == 0)
            {
                toolRes.IsError = true;
                toolRes.Result = "Window size must be odd.";
                return toolRes.ToJson();
            }
            if (polynomialOrder >= windowSize)
            {
                toolRes.IsError = true;
                toolRes.Result = "polynomialOrder can not be larger than windowSize";
                return toolRes.ToJson();
            }
            if (!ioCtrl.ReadData(uploadedFileDir, out var x, out var y))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to read data file";
                return toolRes.ToJson();
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
            if (!ioCtrl.WriteData(x, result, out var tempPath))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to write result file";
                return toolRes.ToJson();
            }
            if (!ioCtrl.WriteVisualizationData(x, new List<IList<double>>() { y, result }, new List<string>() { "Original Data", "Smoothed Data" }, out var resPath))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to write result file";
                return toolRes.ToJson();
            }
            toolRes.Result = tempPath;
            toolRes.VisualizationResult = resPath;
            return toolRes.ToJson();
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
            var toolRes = new ToolExecutionResult() { VisualizationType = VisualizationType.LineChart };
            if (!ioCtrl.ReadData(uploadedFileDir, out var x, out var origSig))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to read data file";
                return toolRes.ToJson();
            }
            double[] corrected = new double[origSig.Count()];
            double[] baseline = new double[origSig.Count()];
            AirPLS_AMPD.airPLS(origSig, corrected, baseline, origSig.Count(), lambda, itermax);
            if (!ioCtrl.WriteData(x, corrected, out var tempPath))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to write result file";
                return toolRes.ToJson();
            }
            if (!ioCtrl.WriteVisualizationData( x, new List<IList<double>>() { origSig, corrected, baseline }, new List<string>() { "Original Data", "Data(no baseline)", "baseline" }, out var resPath))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to write result file";
                return toolRes.ToJson();
            }
            toolRes.Result = tempPath;
            toolRes.VisualizationResult = resPath;
            return toolRes.ToJson();
        }
        [McpServerTool, Description("Read data from uploaded file, and perform Raman analysis on said data based on the database specified by type parameter. type parameter should be specified by user. ")]
        public static string RamanAnalysis(
            DataIO ioCtrl,
            [Description("Uploaded file directory where the uploaded file is")] string uploadedFileDir,
            [Description("The general type of the data in the uploaded file. ")] EnumRamanDBType type)
        {
            var toolRes = new ToolExecutionResult() { VisualizationType = VisualizationType.Table };
            if (!ioCtrl.ReadData(uploadedFileDir, out var x, out var origSig))
            {
                toolRes.IsError = true;
                toolRes.Result = "Failed to read result file";
                return toolRes.ToJson();
            }
            var algRes = Analyzer.Instance.Analyze(type, x.ToList(), origSig.ToList());
            if(algRes.Count == 0)
            {
                toolRes.IsError = true;
                toolRes.Result = "No material found. ";
            }
            else
            {
                toolRes.IsError = false;
                var ramanRes = RamanAnalysisResult.FromMaterialAnalysisResult(algRes.OrderByDescending(r => r.TrustScore), type);
                toolRes.VisualizationResult = ramanRes;
                toolRes.Result = "Success!";
            }
            return toolRes.ToJson();
        }
    }
}
