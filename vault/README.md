# Obsidian Binder — Vault Home

Welcome to your binder. This vault holds a collection of [RAPPcards](https://github.com/kody-w/RAPPcards) — agent identity cards from a federated network — but the cards are markdown notes you can read, search, and connect like any other notes in your second brain.

## How this vault works

- Each card lives in [[cards/]] as one markdown note
- Frontmatter holds the federation-required fields (seed, incantation, name, agent_id)
- The body is yours — write whatever you want about the card
- Use `[[wiki-links]]` to connect cards in the graph view
- Tag with `#insight`, `#wishlist`, `#archived`, or whatever fits your thinking

## Summoning new cards

1. Open `binder.html` in your browser (it's in this vault root)
2. Paste a 7-word incantation
3. The federation walker fetches the card from whichever peer owns it
4. A new markdown note is created in `cards/` with frontmatter pre-populated
5. Add your notes to the body
6. Commit — the GitHub Action regenerates the federation files

## Reading your binder

The way you'd read any Obsidian vault:

- **Graph view** to see how your cards connect via backlinks
- **Search** for full-text across all your card notes
- **Tags pane** to slice your collection by your own taxonomy
- **Daily notes** to log when you summoned what and why

You already know how to use this. The federation just works underneath.

## Essays

[[essays/why-i-keep-my-binder-in-obsidian]] — the manifesto

## The cards

See `cards/` for the full collection.
