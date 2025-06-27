using RamanAnalyzeModel.Model;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace McpServer
{
    public class RamanAnalysisResult
    {
        public List<string> Images { get; set; } = new List<string>() { };
        public List<string> Name { get; set; } = new List<string>() { };
        public List<string> ChemicalFormulas { get; set; } = new List<string>() { };
        public List<double> TrustScores { get; set; } = new List<double>() { };
        public static RamanAnalysisResult FromMaterialAnalysisResult(IEnumerable<MaterialAnalyseResult> matResults)
        {
            var res = new RamanAnalysisResult()
            {
                Name = new List<string>(matResults.Count()),
                ChemicalFormulas = new List<string>(matResults.Count()),
                TrustScores = new List<double>(matResults.Count()),
                Images = new List<string>(matResults.Count()),
            };
            int counter = 0;
            foreach (var matResult in matResults)
            {
                res.Name.Add(matResult.SampleName);
                res.ChemicalFormulas.Add(matResult.Formula);
                res.TrustScores.Add(matResult.TrustScore / 100);
                if(string.IsNullOrEmpty(matResult.ImagePath))
                {
                    res.Images.Add("None");
                }
                else
                {
                    //res.Images.Add($"![]({"./good_images/" + Path.GetFileName(matResult.ImagePath)})");
                    res.Images.Add($"{"http://192.168.108.24:41100/" + Path.GetFileName(matResult.ImagePath)}");
                    //res.Images.Add("https://i.imgur.com/fH2LHvo.png");
                    //res.Images.Add(matResult.ImagePath.Replace('\\','/'));
                }
                counter++;
                if(counter > 10)
                {
                    break;
                }
            }

            return res;
        }
        public string ToMarkdownTable()
        {
            var sb = new StringBuilder();
            sb.AppendLine("|Name|Chemical Formula|Trust Score|Image|");
            sb.AppendLine("|:---|:---|:---|:---|");
            for(int i = 0; i < Name.Count; i++)
            {
                sb.AppendLine($"|{Name[i]}|{ChemicalFormulas[i]}|{TrustScores[i]}|{Images[i]}|");
            }
            return sb.ToString();
        }
    }
}
