# .NET testing notes

## Running tests
- One test: `dotnet test --filter "FullyQualifiedName~NoteTests.Rejects_title_over_80_chars"`
- One project: `dotnet test tests/Notes.Api.Tests`
- Everything: `dotnet test`
- CI compiles with warnings as errors: `dotnet build -warnaserror`.

## Tools
- **Framework:** xUnit by default. If the project uses NUnit or MSTest, follow it.
- **Clock:** take a `TimeProvider` as a constructor argument. Tests pass a `FakeTimeProvider` (from `Microsoft.Extensions.TimeProvider.Testing`) and move it with `Advance(...)`.
- **Parameterised tests:** `[Theory]` plus `[InlineData]`.
- **Architecture rules:** ArchUnitNET or NetArchTest.

## Integration tests
- Host the real app with `WebApplicationFactory<Program>`. Use `IClassFixture<WebApplicationFactory<Program>>`, or a subclass. Override only the true externals, inside `ConfigureWebHost`.
- Give each test class its own database through a class fixture. Create it fresh and apply every migration. Testcontainers or local services both work.
- Sign test users in with helper methods. Assert the status code and the exact body.
- Count queries with a command interceptor. Reset the counter before the request. Assert the exact count for one item and again for several. That catches N+1.

## Sample
```csharp
public class NoteTitleTests
{
    [Theory]
    [InlineData(80, true)]
    [InlineData(81, false)]
    public void Title_allows_at_most_80_characters(int length, bool expected)
    {
        var allowed = Note.TitleFits(new string('a', length));

        Assert.Equal(expected, allowed);
    }
}
```
