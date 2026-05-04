namespace LaadinfrastructuurPlanner.Services;

public sealed class RouteAnalysisOptions
{
    public required string RepoRoot { get; init; }
    public required string CacheDir { get; init; }
    public required string UploadedDatasetDir { get; init; }
    public required string DuckDbPath { get; init; }
    public required string ManifestPath { get; init; }
    public string? OriginalCsvDir { get; init; }
    public string? ExternalCacheDir { get; init; }
    public string? ZeZonesSourcePath { get; init; }
}

public static class RouteAnalysisOptionsFactory
{
    public static RouteAnalysisOptions FromContentRoot(string contentRoot)
    {
        var configuredRoot = Environment.GetEnvironmentVariable("ROUTE_ANALYSIS_REPO_ROOT");
        var repoRoot = !string.IsNullOrWhiteSpace(configuredRoot)
            ? Path.GetFullPath(configuredRoot)
            : Path.GetFullPath(Path.Combine(contentRoot, "..", ".."));
        var cacheDir = Path.Combine(repoRoot, ".cache");
        var plannerCacheDir = Path.Combine(cacheDir, "planner");
        var originalCsvDir = Environment.GetEnvironmentVariable("ROUTE_ANALYSIS_ORIGINAL_CSV_DIR");
        var externalCacheDir = Environment.GetEnvironmentVariable("ROUTE_ANALYSIS_EXTERNAL_CACHE_DIR");
        var zeZonesSourcePath = Environment.GetEnvironmentVariable("ROUTE_ANALYSIS_ZE_ZONES_PATH");

        return new RouteAnalysisOptions
        {
            RepoRoot = repoRoot,
            CacheDir = cacheDir,
            UploadedDatasetDir = Path.Combine(cacheDir, "uploaded-dataset", "active"),
            DuckDbPath = Path.Combine(plannerCacheDir, "route-analysis.duckdb"),
            ManifestPath = Path.Combine(plannerCacheDir, "manifest.json"),
            OriginalCsvDir = FirstExistingDirectory(originalCsvDir),
            ExternalCacheDir = FirstExistingDirectory(externalCacheDir),
            ZeZonesSourcePath = FirstExistingFile(zeZonesSourcePath),
        };
    }

    private static string? FirstExistingDirectory(params string?[] candidates)
    {
        return candidates.FirstOrDefault(path => !string.IsNullOrWhiteSpace(path) && Directory.Exists(path));
    }

    private static string? FirstExistingFile(params string?[] candidates)
    {
        return candidates.FirstOrDefault(path => !string.IsNullOrWhiteSpace(path) && File.Exists(path));
    }
}
