using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace McpServer
{
    /// <summary>
    /// 
    /// </summary>
    public partial class AirPLS_AMPD
    {
        [DllImport("airpls_ampd.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int airPLS(double[] signal, double[] signal_corr, double[] baseline, int signal_size, double lambda_, int itermax);
        [DllImport("airpls_ampd.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int AMPD(double[] signal, int signal_length, ref PeakStruct peak_info);
        [DllImport("airpls_ampd.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern void cleanup(ref PeakStruct mystruct);
    }

    public struct PeakStruct
    {
        public int peak_num;
        public IntPtr peak_index; // 使用IntPtr来存储指针
    }
}
