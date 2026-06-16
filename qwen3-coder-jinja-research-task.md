# Qwen3-Coder-30B-A3B-Instruct Jinja Research Task

## Ziel

Diese Aufgabe dient dazu, für **Qwen3-Coder-30B-A3B-Instruct** alle auffindbaren Jinja-/Chat-Templates systematisch zu sammeln, deren Zielsetzung zu klassifizieren, die berichteten Fixes und Optimierungen auszuwerten und daraus ein belastbares, auf **Cline** ausgerichtetes `chat_template.jinja` abzuleiten.[cite:58][cite:3][cite:2]

Der Fokus liegt ausdrücklich auf **realen Erfolgsmeldungen** und **praktischer Reproduzierbarkeit** in lokalen Agent-Setups, nicht nur auf theoretisch korrekten Templates.[cite:3][cite:49]

## Ausgangslage

Qwen3-Coder-30B-A3B-Instruct hatte im Feld mehrfach Probleme mit Tool-Calling, insbesondere wenn lokale Clients die Modellausgabe **wörtlich als Text** statt als echten Tool-Call behandelten.[cite:49][cite:3] Gleichzeitig existieren mehrere konkurrierende Template-Richtungen: das originale Qwen-Template, ein offizielles Qwen-Update als Pull Request, die Unsloth-Fix-Serie, communitygebaute XML/JSON-Hybride sowie Ollama-Templates mit JSON-in-XML-Wrappern.[cite:58][cite:61][cite:2][cite:59]

## Zu sammelnde Templates

### 1. Originales Qwen-Template

- Quelle: offizielles Modell `Qwen/Qwen3-Coder-30B-A3B-Instruct`.[cite:58]
- Aufgabe: die aktuelle im Modell referenzierte `chat_template.jinja` bzw. die Version aus `tokenizer_config.json` erfassen.[cite:58]
- Wichtig: Pull Request #28 dokumentiert ein offizielles Update des Templates und zeigt, welche Strukturänderungen Qwen selbst in Richtung Tool-Spezifikation vorgenommen hat.[cite:58]

### 2. Qwen PR #28 Update

- Quelle: `Qwen/Qwen3-Coder-30B-A3B-Instruct · Update chat_template.jinja`.[cite:58]
- Extrahiere die Absicht hinter den Änderungen:
  - Werkzeugbeschreibung wurde ausführlicher gemacht.[cite:58]
  - Parameter werden stärker strukturiert gerendert (`<name>`, Typ, Beschreibung, Enum, Required-Felder).[cite:58]
  - Behandlung von Argumentwerten wurde vereinfacht (`string` statt aggressiver `tojson safe`-Serialisierung in manchen Stellen).[cite:58]
- Prüfe, ob die PR als **Stabilitätsfix**, **Kompatibilitätsfix** oder **Prompt-Qualitätsverbesserung** zu lesen ist.[cite:58]

### 3. Unsloth-Fix / neue Chat-Templates

- Quelle: Unsloth Diskussion „New Chat Template + Tool Calling Fixes as of 05 Aug, 2025“.[cite:3]
- Erfasse:
  - Behauptetes Ziel: Tool-Calling-Reliabilität verbessern, nachdem frühere Fixes nur in manchen Setups funktionierten.[cite:3]
  - Behauptete Reichweite: „extensive testing“ intern und extern, deutlich bessere Stabilität.[cite:3]
  - Einschränkung: laut Unsloth seien für korrektes Tool-Calling ihre Quants nötig; diese Aussage ist zu dokumentieren, aber empirisch gegenzuprüfen.[cite:3]
- Notiere die gemeldeten Ergebnisse:
  - Positive Berichte in RooCode/LM Studio/OpenWebUI-Setups.[cite:3]
  - Negative oder gemischte Ergebnisse in Qwen Code, Codex, Opencode, Crush oder llama.cpp-only-Setups.[cite:3]

### 4. Community-Template aus alter Qwen3-Diskussion

- Quelle: Unsloth-Diskussion verweist auf ein älteres `qwen3-chat-template.jinja`, das „für ein paar Calls“ mit RooCode und llama.cpp funktioniere.[cite:3]
- Aufgabe: Wenn auffindbar, die Datei sichern und als **historischen Zwischenstand** markieren.[cite:3]

### 5. mostlygeek-Template

- Quelle: Gist `qwen3-coder-30B jinja template, works with Claude Code`.[cite:2]
- Kernaussage dokumentieren:
  - Fokus auf XML-artige Tool-Aufrufe mit `<tool_call>`, innerem `<function=...>`-Block und `<parameter=...>`-Blöcken.[cite:2]
  - Primärer Zielclient ist Claude Code, nicht Cline.[cite:2]
- Prüfen:
  - Welche Teile sind client-neutral?
  - Welche Teile sind vermutlich Claude-Code-spezifisch und für Cline eher hinderlich?

### 6. Ollama/Modelfile-Template mit JSON-in-XML

- Quelle: Ollama Blob `mdq100/Qwen3-Coder-30B-A3B-Instruct:30b/template`.[cite:59]
- Kerneigenschaften:
  - Tools werden als JSON in `<tools>` ausgegeben.[cite:59]
  - Tool-Calls werden als JSON-Objekt in `<tool_call>...</tool_call>` erwartet.[cite:59]
- Diese Richtung ist für Cline besonders interessant, weil viele Harnesses JSON leichter parsen als freie XML-Strukturen.[cite:59][cite:3]

### 7. Embedded/Repo-Template von Unsloth

- Quelle: `unsloth/Qwen3-Coder-30B-A3B-Instruct/blame/.../chat_template.jinja`.[cite:61]
- Aufgabe: soweit abrufbar, den eingebetteten Stand dokumentieren und mit der Diskussion #10 abgleichen.[cite:61][cite:3]

## Bewertungsraster pro Template

Für **jedes Template** eine Matrix anlegen:

| Feld                      | Beschreibung                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| Name                      | Eindeutige Bezeichnung                                                                         |
| Quelle                    | URL / Repo / Gist                                                                              |
| Herkunft                  | Qwen / Unsloth / Community / Ollama / Sonstiges                                                |
| Zielclient                | Qwen Code / Claude Code / RooCode / Cline / OpenCode / generisch                               |
| Tool-Format               | XML, JSON-in-XML, reines JSON, Hybrid                                                          |
| Prompt-Stil               | kompakt, verbose, schemaorientiert, agentenorientiert                                          |
| Fix-/Optimierungsrichtung | z. B. Parser-Kompatibilität, Required-Parameter, Mehrschritt-Tool-Use, weniger Halluzinationen |
| Erfolgsberichte           | konkrete positive Erfahrungswerte                                                              |
| Fehlermuster              | konkrete negative Berichte                                                                     |
| Risiko für Cline          | niedrig / mittel / hoch                                                                        |
| Eignung für OVMS Override | niedrig / mittel / hoch                                                                        |

Alle Bewertungen müssen mit Inline-Zitaten belegt werden.[cite:58][cite:3][cite:2][cite:59][cite:49]

## Was als Erfolg zählt

Ein Template gilt nur dann als **plausibel erfolgreich**, wenn mindestens eines der folgenden Signale vorliegt:

- ein Nutzer berichtet, dass ein realer Agent-Workflow vollständig lief, z. B. Dateien lesen, schreiben, Tests ausführen, Fehler beheben.[cite:3]
- das Modell nutzt Tools konsistent und nicht nur als sichtbaren Text im Chat.[cite:49][cite:3]
- das Template wurde in einem realen Client wie RooCode, Continue, LM Studio, OpenWebUI oder ähnlichem mit nachvollziehbarer Konfiguration eingesetzt.[cite:3][cite:49]

**Nicht ausreichend** sind:

- bloße Behauptungen ohne Testkontext,[cite:3]
- nur „scheint besser“ ohne reproduzierbare Angaben,[cite:3]
- rein syntaktische Plausibilität des Templates ohne echte Tool-Ausführung.[cite:49]

## Priorisierte Hypothesen für Cline

Die Recherche soll diese Hypothesen prüfen:

1. **Cline profitiert eher von JSON-in-XML als von freiem XML mit variablen Tag-Namen.** Dafür spricht, dass mehrere Nutzer bei Qwen3-Coder Probleme mit unerwarteten XML-Formaten und sichtbaren Sondertags berichteten.[cite:3][cite:49]
2. **Viele Fehler sind Client-/Parser-Mismatches, nicht nur Modellfehler.** Continue-Nutzer berichteten, dass Tool-Strukturen literal ausgegeben statt ausgeführt wurden.[cite:49]
3. **Ein gutes Cline-Template sollte minimalistisch und parserfreundlich sein.** Je mehr Spezialformatierung, desto höher das Risiko von Fehlinterpretation in OpenAI-kompatiblen Bridges oder Client-Parsers.[cite:59][cite:3]
4. **Qwen/Unsloth-Templates mit aggressivem XML-Schema können für Qwen Code oder Claude Code brauchbar sein, aber für Cline unnötig komplex.** Diese These anhand der Communityberichte prüfen.[cite:2][cite:3]

## Teststrategie für die KI

Die KI soll nicht nur ein Template schreiben, sondern es **eigenständig testbar** machen.

### A. Minimaler Harness-Test

Ein lokaler Test sollte einen OpenAI-kompatiblen Endpoint gegen das Modell senden und nur **ein** Tool bereitstellen, z. B. `read_file` oder `echo`.[cite:49]

Pflicht-Testfälle:

1. **Single tool call**: Modell soll ein Tool exakt einmal aufrufen.
2. **Structured args**: Argumente müssen gültiges JSON sein.
3. **Tool result follow-up**: Nach Tool-Antwort soll das Modell sinnvoll weiterarbeiten.
4. **No-tool answer**: Ohne passenden Tool-Bedarf darf kein Fake-Tool-Call generiert werden.

### B. Cline-naher Verhaltenstest

Da Cline ein Coding-Agent ist, soll die KI zusätzlich einen **Workspace-Test** formulieren:

- Aufgabe: „Lies `README.md`, finde eine TODO-Markierung, erstelle `hello.txt`, bestätige den Inhalt.“
- Erfolgsbedingung: Das Modell ruft die passenden Tools auf, statt die Aufrufe als Text darzustellen.[cite:49][cite:3]

### C. CI-/Headless-Idee

Es gibt in den recherchierten Quellen keinen belastbaren Nachweis für ein offizielles **`cline-ci`**-Produkt; diese Abwesenheit ist offen zu dokumentieren.[cite:49] Die Recherche soll daher stattdessen nach einem **headless oder skriptbaren Cline-Testpfad** suchen und, falls keiner existiert, einen alternativen automatisierten Harness mit HTTP-Requests vorschlagen.[cite:49]

## Konkreter Arbeitsauftrag

1. Sammle alle verfügbaren Templates aus den oben genannten Quellen und speichere sie lokal.
2. Vergleiche sie strukturell.
3. Ordne jeder Variante Ziel, Fixrichtung und berichtete Resultate zu.
4. Bestimme, welches Muster für **Cline** am wahrscheinlichsten robust ist.
5. Erzeuge daraus ein neues `chat_template.jinja`, optimiert für:
   - OpenAI-kompatiblen lokalen Server,
   - JSON-in-XML Tool-Calls,
   - möglichst einfache Parser-Interoperabilität,
   - mehrstufige Tool-Nutzung.
6. Implementiere einen reproduzierbaren lokalen Testplan.
7. Falls möglich, liefere kleine Testskripte mit `curl` oder Python, damit die Implementierung automatisch verifiziert werden kann.[cite:49][cite:59]

## Erwartetes Endergebnis

Das Endergebnis soll enthalten:

- eine Tabelle aller gefundenen Qwen3-Coder-30B-A3B-Instruct-Jinjas,[cite:58][cite:3][cite:2][cite:59][cite:61]
- eine Bewertung der Erfolgsberichte und Misserfolge,[cite:3][cite:49]
- ein Cline-orientiertes Template,
- eine Begründung, warum genau dieses Format für Cline gewählt wurde,[cite:59][cite:49]
- eine lokale Testanleitung, die ohne manuelle IDE-Klickerei möglichst viel automatisch prüft.[cite:49]

## Vorläufige Schlussfolgerung aus dem aktuellen Stand

Die derzeit beste Ausgangsbasis für **Cline** ist wahrscheinlich **nicht** das Claude-Code-orientierte mostlygeek-Template, sondern eher ein **reduziertes JSON-in-XML-Modell** ähnlich der Ollama-Variante, weil dieses Format für Client-Parser leichter auszuwerten ist und besser zu OpenAI-kompatiblen Tool-Chains passt.[cite:2][cite:59][cite:49] Gleichzeitig müssen die positiven RooCode-/LM-Studio-Berichte aus der Unsloth-Diskussion berücksichtigt werden, da sie zeigen, dass Template, Laufzeit und Client gemeinsam über Erfolg oder Misserfolg entscheiden.[cite:3]
