# Field-note this page bookmarklets

Drag one link to the browser's bookmarks bar, then use it on a Wikipedia page,
newspaper article, or other public source. Each carries the current page title
and URL into a fresh, editable Field Notes request. The prompt is prefilled —
review it and send it yourself.

| Choose | Bookmarklet | Notes |
|---|---|---|
| ChatGPT web | [Field-note in ChatGPT](javascript:(()=>{const%20prompt=`Use%20the%20field-notes%20skill%20to%20turn%20this%20source%20into%20an%20editable,%20cited%20Field%20Notes%20sheet%20or%20notebook.%20Read%20the%20source%20first,%20choose%20the%20right%20route%20and%20variant,%20and%20keep%20a%20visible%20source%20link.%5Cn%5Cn${document.title}%5Cn${location.href}`;window.open(`https://chatgpt.com/?q=${encodeURIComponent(prompt)}`,`_blank`,`noopener`)})()) | Opens a new browser tab. This is the portable default. |
| Claude Desktop | [Field-note in Claude](javascript:(()=>{const%20prompt=`Use%20the%20field-notes%20skill%20to%20turn%20this%20source%20into%20an%20editable,%20cited%20Field%20Notes%20sheet%20or%20notebook.%20Read%20the%20source%20first,%20choose%20the%20right%20route%20and%20variant,%20and%20keep%20a%20visible%20source%20link.%5Cn%5Cn${document.title}%5Cn${location.href}`;location.href=`claude://claude.ai/new?q=${encodeURIComponent(prompt)}`})()) | Opens a new Claude Desktop chat, when installed. |
| Codex Desktop | [Field-note in Codex](javascript:(()=>{const%20source=location.href;const%20prompt=`Use%20the%20field-notes%20skill%20to%20turn%20this%20source%20into%20an%20editable,%20cited%20Field%20Notes%20sheet%20or%20notebook.%20Read%20the%20source%20first,%20choose%20the%20right%20route%20and%20variant,%20and%20keep%20a%20visible%20source%20link.%5Cn%5Cn${document.title}%5Cn${source}`;location.href=`codex://threads/new?prompt=${encodeURIComponent(prompt)}&originUrl=${encodeURIComponent(source)}`})()) | Opens a new local Codex thread when the desktop handler supports it. |

`claude://claude.ai/new?q=…` is Anthropic's documented Claude Desktop link
format. `https://chatgpt.com/?q=…` is a web hand-off that pre-fills ChatGPT,
but not a published OpenAI integration contract. `codex://threads/new` is
available in the installed Codex desktop app, but its prompt and origin
parameters are not yet published OpenAI deep-link documentation; treat that
option as version-dependent.

The `claude:///` form may launch the app, but use the complete
`claude://claude.ai/new?q=…` format above to target a new prefilled chat. If a
source is paywalled or unavailable to the selected assistant, paste the
relevant text instead of asking the skill to invent missing facts.
