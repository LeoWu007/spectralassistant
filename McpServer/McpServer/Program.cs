using McpServer;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using ModelContextProtocol.Server;
using System.ComponentModel;
using System.Net.Http.Headers;

//var builder = Host.CreateApplicationBuilder(args);
var builder = WebApplication.CreateBuilder(args);
builder.WebHost.ConfigureKestrel(option =>
{
    option.ListenLocalhost(3001);
});

builder.Services.AddMcpServer()
    //.WithStdioServerTransport()
    .WithTools<McpTools>();

builder.Logging.AddConsole(options =>
{
    options.LogToStandardErrorThreshold = LogLevel.Trace;
});

builder.Services.AddSingleton<DataIO>();

var app = builder.Build();
app.MapMcp();
app.Run();