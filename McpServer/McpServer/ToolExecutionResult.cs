using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace McpServer
{
    public enum VisualizationType
    {
        None = 0,
        LineChart = 1,
        Table = 2
    }
    public class ToolExecutionResult
    {
        public bool IsError { get; set; } = false;
        public object? Result { get; set; } = null;
        public object? VisualizationResult { get; set; } = null;
        public required VisualizationType VisualizationType { get; set; } = VisualizationType.None;
        public string ToJson()
        {
            return JsonConvert.SerializeObject(this, new JsonSerializerSettings
            {
                Formatting = Formatting.None
            });
        }
    }
}
