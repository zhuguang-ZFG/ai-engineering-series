# Omp volume: English translation pending

The [Chinese manuscript](../../omp/README.md) is the source of truth for this volume.
This directory reserves the English edition; it does not contain translated chapters or a buildable edition.

The current manifest keeps `langs: ["zh"]` and the output prefix `yuyu-omp`.
Enabling English requires translations for the foreword, all 33 chapters and five appendices, followed by
English guides, glosses, notes, reading paths and illustration labels. Every unit must declare an English
source path before `en` is added to the manifest's language list.

The translation must pass structure, reference and language checks, including the prohibition on untranslated
Chinese prose. See [product configuration](../../yuyu-book/PRODUCTS.md) and
[build instructions](../../omp/BUILD.md) for the activation checklist.
