# quayside

Docker is awesome. And a very handy use case of Docker is that it allows to wrap commands that are somewhat difficult to set up in a container that comes with all the dependencies pre-configured. This approach however, comes with the downside that calling Docker is usually a bit more complicated that just calling a local command.

This is where quayside comes in. The goal of this app is to provide a simple wrapper for a limited but very repetitive use case.

## Example usage

An example of a tool, that is offered as a container is [sslyze](https://github.com/nabla-c0d3/sslyze).

A common call would look like this:

```
docker run --rm -v "$(pwd):/data/" nablac0d3/sslyze:5.0.0 www.google.com --json_out /data/result.json
```

To do the same via quayside we need to define sslyze in a file called `quayside.yaml`:

```yaml
sslyze:
  container: nablac0d3/sslyze:5.0.0
  cwd: /data/
  mapped_arguments:
    cwd:
      - "--json_out"
      - "--targets_in"
      - "--cert"
      - "--key"
      - "--keyform"
      - "--pass"
```

Now we can call sslyze like this:

```
quayside sslyze --json_out=result.json www.google.com
```

The current working directory is automatically mounted at `/data/` and paths that are passed to one of the *mapped arguments* are interpreted relative to that folder.
