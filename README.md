# Smart Campus Room Availability Checker — Assignment 03

One responsive page for fictional room A-102. Checks availability only; booking data is read-only.

- [Public working demo](https://bdaniyar.github.io/boltnew3assSE/)
- [Original Bolt.new project](https://bolt.new/~/sb1-bskzikuu)
- [GitHub repository](https://github.com/bdaniyar/boltnew3assSE)
- [Submission files, evidence and setup](A3_Boranov_Daniyar/README.md)
- [Report](A3_Boranov_Daniyar/A3_Boranov_Daniyar_Report.pdf)
- [AI evidence](A3_Boranov_Daniyar/AI_Evidence.pdf)

## Local setup and checks

Use Python 3 and Node.js 20.19+ or 22.12+.

```sh
npm ci
npm run dev
```

```sh
python3 -m unittest -v test_booking
npm test
npm run lint
npm run typecheck
npm run build
```

Executed results: Python 47/47; frontend logic 37/37. Rendered checks cover all six mandatory scenarios, ten additional boundaries, eight repair checks, and four widths. All six mandatory scenarios also passed on the public demo.

## Original version and publication

The original Bolt source is preserved at tag `prototype-v1`, commit `687c5f7bbcb29590ad3030cf5e596431be5971b7`, and in the submission archive. The final prototype retains the original React, TypeScript, Vite and Tailwind structure.

GitHub Pages hosts the verified production build from `gh-pages`; pushing `main` alone does not update this hosted snapshot or prove Bolt synchronization. The repository remains private, and the complete source is included in the submission package.

Bolt publication is unverified because its WebContainer failed to boot. Open the original Bolt project in a working Chromium session, load or sync the latest GitHub `main`, verify the `prototype v2` footer and read-only bookings, then select **Publish** and test the Bolt-hosted URL. The GitHub Pages demo above is already public and verified.

Final audit: six remaining dependency advisories (two low, three moderate, one high). Full logs and verification limits are in the submission evidence.
