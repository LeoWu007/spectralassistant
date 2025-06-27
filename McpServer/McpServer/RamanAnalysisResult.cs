using RamanAnalyzeModel.Model;
using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace McpServer
{
    public class RamanAnalysisResult
    {
        private const string WheatImageTemplate = "Wheat_{0}.jpg";
        private const string AerospaceImageTemplate = "Aero_{0}.jpg";
        private const string AlcoholImageTemplate = "Alcohol_{0}.jpg";
        private const string BiologyImageTemplate = "Bio_{0}.jpg";
        private const int WheatImageNum = 2;
        private const int AerospaceImageNum = 2;
        private const int AlcoholImageNum = 2;
        private const int BiologyImageNum = 3;
        public List<string> Images { get; set; } = new List<string>() { };
        public List<string> Name { get; set; } = new List<string>() { };
        public List<string> ChemicalFormulas { get; set; } = new List<string>() { };
        public List<double> TrustScores { get; set; } = new List<double>() { };
        public static RamanAnalysisResult FromMaterialAnalysisResult(IEnumerable<MaterialAnalyseResult> matResults, EnumRamanDBType type)
        {
            var res = new RamanAnalysisResult()
            {
                Name = new List<string>(matResults.Count()),
                ChemicalFormulas = new List<string>(matResults.Count()),
                TrustScores = new List<double>(matResults.Count()),
                Images = new List<string>(matResults.Count()),
            };
            foreach (var matResult in matResults)
            {
                res.Name.Add(matResult.SampleName);
                res.ChemicalFormulas.Add(matResult.Formula);
                res.TrustScores.Add(matResult.TrustScore / 100);
                if (string.IsNullOrEmpty(matResult.ImagePath))
                {
                    var dir = "C:\\Users\\Win10ProAI\\Desktop\\McpDemo\\mcpdemo\\McpClient\\good_images";
                    var rng = new Random(Guid.NewGuid().GetHashCode());
                    switch (type)
                    {
                        case EnumRamanDBType.Agriculture:
                            var num = rng.Next(1, WheatImageNum);
                            res.Images.Add($"{"http://192.168.241.210:41101/" + string.Format(WheatImageTemplate, num)}");
                            break;
                        case EnumRamanDBType.Biont:
                            num = rng.Next(1, BiologyImageNum);
                            res.Images.Add($"{"http://192.168.241.210:41101/" + string.Format(BiologyImageTemplate, num)}");
                            break;
                        case EnumRamanDBType.Liquor:
                            num = rng.Next(1, AlcoholImageNum);
                            res.Images.Add($"{"http://192.168.241.210:41101/" + string.Format(AlcoholImageTemplate, num)}");
                            break;
                        case EnumRamanDBType.Spaceflight:
                            num = rng.Next(1, AerospaceImageNum);
                            res.Images.Add($"{"http://192.168.241.210:41101/" + string.Format(AerospaceImageTemplate, num)}");
                            break;
                        default:
                            res.Images.Add("None");
                            break;
                    }
                }
                else
                {
                    //res.Images.Add($"![]({"./good_images/" + Path.GetFileName(matResult.ImagePath)})");
                    res.Images.Add($"{"http://192.168.241.210:41101/" + Path.GetFileName(matResult.ImagePath)}");
                    //res.Images.Add("https://i.imgur.com/fH2LHvo.png");
                    //res.Images.Add(matResult.ImagePath.Replace('\\','/'));
                }
            }

            return res;
        }
        public string ToMarkdownTable()
        {
            var sb = new StringBuilder();
            sb.AppendLine("|Name|Chemical Formula|Trust Score|Image|");
            sb.AppendLine("|:---|:---|:---|:---|");
            for (int i = 0; i < Name.Count; i++)
            {
                sb.AppendLine($"|{Name[i]}|{ChemicalFormulas[i]}|{TrustScores[i]}|{Images[i]}|");
            }
            return sb.ToString();
        }
    }
}
