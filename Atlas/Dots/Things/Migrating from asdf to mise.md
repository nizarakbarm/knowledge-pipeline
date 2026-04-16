---
created: 2026-04-15
up:
  - "[[Mise]]"
related:
  - "[[asdf]]"
in:
  - "[[Atlas]]"
tags:
  - mise
  - asdf
  - migration
  - dev-tools
---

# Migrating from asdf to mise

## Summary
Migrating from asdf to mise involves installing mise, setting up shell activation, removing asdf from your configuration, and letting mise take over existing `.tool-versions` files. There is no longer a reason to prefer asdf to mise, and mise provides a more secure experience [cite: 83][cite: 89].

## Key Points
- There is no longer a reason to prefer asdf to mise; users should migrate [cite: 83].
- mise provides a more secure experience compared to asdf [cite: 89].
- mise reads existing asdf `.tool-versions` files without modification.
- mise uses `~/.config/mise/config.toml` for global configuration instead of `~/.tool-versions`.

## Details

### 1. Install mise

Install mise via the official install script [cite: 67]:

```shell
curl https://mise.run | sh
```

By default, this installs to `~/.local/bin`. Verify the installation:

```shell
~/.local/bin/mise --version
# mise 2024.x.x
```

### 2. Set up `mise activate`

Add the activation command to your shell's rc file so mise updates `PATH` and environment variables automatically [cite: 67]:

**bash:**
```shell
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
```

**zsh:**
```shell
echo 'eval "$(~/.local/bin/mise activate zsh)"' >> ~/.zshrc
```

**fish:**
```shell
echo '~/.local/bin/mise activate fish | source' >> ~/.config/fish/config.fish
```

Restart your shell session after modifying your rc file. Then run `mise doctor` to verify the setup.

### 3. Remove asdf from your shell rc file

Remove the lines that initialize asdf from your shell configuration [cite: 67].

### 4. Install tools from existing `.tool-versions`

Run `mise install` in any directory that contains an asdf `.tool-versions` file, and mise will install the specified tools automatically [cite: 67]:

```shell
mise install
```

### 5. Migrate global `.tool-versions` to mise (optional)

Unlike asdf, mise does not treat `~/.tool-versions` as a global config file. It uses `~/.config/mise/config.toml` for global configuration. To migrate your global `.tool-versions` file, run:

```shell
mv ~/.tool-versions ~/.tool-versions.bak
cat ~/.tool-versions.bak | tr -s ' ' | tr ' ' '@' | xargs -n2 mise use -g
```

### 6. Remove backup and uninstall asdf

Once you are comfortable with mise, remove the `.tool-versions.bak` file and uninstall asdf to complete the migration [cite: 69]:

```shell
rm ~/.tool-versions.bak
```

## Connections
- **Questions this raises:** How does mise handle plugin compatibility compared to asdf?
- **Related to:** [[Mise]], [[asdf]], [[Development Environment MOC]]
- **Applies to:** Upgrading local development workflows, team tooling standardization

## Sources
- [How do I migrate from asdf? — mise FAQ](https://mise.jdx.dev/faq.html#how-do-i-migrate-from-asdf)
- [Getting Started — mise](https://mise.jdx.dev/getting-started.html)
