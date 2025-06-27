using McpServer;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Net.Http.Headers;
using System.Text.Json;

//var builder = Host.CreateApplicationBuilder(args);
var algBuilder = WebApplication.CreateBuilder(args);
algBuilder.WebHost.ConfigureKestrel(option =>
{
    option.ListenLocalhost(3001);
});

algBuilder.Services.AddMcpServer()
    //.WithStdioServerTransport()
    .WithTools<AlgorithmTools>();

algBuilder.Logging.AddConsole(options =>
{
    options.LogToStandardErrorThreshold = LogLevel.Trace;
});

algBuilder.Services.AddSingleton<DataIO>();

var algorithmApp = algBuilder.Build();
algorithmApp.MapMcp();

var importBuilder = WebApplication.CreateBuilder(args);
importBuilder.WebHost.ConfigureKestrel(option =>
{
    option.ListenLocalhost(3002);
});
importBuilder.Services.AddMcpServer().WithTools<DataImportTools>();
importBuilder.Logging.AddConsole(options =>
{
    options.LogToStandardErrorThreshold = LogLevel.Trace;
});
importBuilder.Services.AddSingleton<DataIO>();

var importApp = importBuilder.Build();
importApp.MapMcp();

Task.WhenAll(algorithmApp.RunAsync(), importApp.RunAsync()).Wait();