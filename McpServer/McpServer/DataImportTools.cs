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
    public sealed class DataImportTools
    {
        [McpServerTool, Description("Convert data from uploaded file to reasonable format. Result contains path to the output file")]
        public static string ConvertUploadedFile(
            [Description("Path of the input file")] string filePath,
            [Description("Number of non-data rows to skip")] int rowsToSkip,
            [Description("Number of non-data columns to skip")] int columnsToSkip)
        {
            var toolRes = new ToolExecutionResult() { VisualizationType = VisualizationType.None };
            var xList = new List<double>(4096);
            var yList = new List<double>(4096);
            using (var sr = new StreamReader(filePath))
            {
                for (int i = 0; i < rowsToSkip; i++)
                {
                    sr.ReadLine();
                }
                while (!sr.EndOfStream)
                {
                    var line = sr.ReadLine()?.Split(',');
                    if (line == null)
                    {
                        toolRes.IsError = true;
                        toolRes.Result = "Null line detected";
                        break;
                    }
                    try
                    {
                        var x = Convert.ToDouble(line[columnsToSkip]);
                        var y = Convert.ToDouble(line[columnsToSkip + 1]);
                        xList.Add(x);
                        yList.Add(y);
                    }
                    catch (Exception)
                    {
                        continue;
                    }
                }
            }
            var outputDir = Path.GetDirectoryName(filePath);
            var name = Path.GetFileNameWithoutExtension(filePath) + "_formatted";
            var extension = Path.GetExtension(filePath);
            var outputPath = Path.Combine(outputDir, name + extension);
            using (var sw = new StreamWriter(outputPath, false, Encoding.UTF8))
            {
                for (int i = 0; i < xList.Count; i++)
                {
                    sw.WriteLine($"{xList[i]},{yList[i]}");
                }
            }
            toolRes.IsError = false;
            toolRes.Result = outputPath;
            return toolRes.ToJson();
        }
    }
}
