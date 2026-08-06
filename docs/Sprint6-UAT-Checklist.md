# Sprint 6 User Acceptance Test Checklist

Use a non-production customer and test order. Record a screenshot or video beside each run.

| ID | Scenario | Expected result | Local result | Production retest |
| --- | --- | --- | --- | --- |
| UAT-01 | Register with valid details | Account created and signed in | Pass | Pending deployment |
| UAT-02 | Reject duplicate/invalid registration | Clear safe error; no account duplication | Pass | Pending deployment |
| UAT-03 | Sign in, sign out, restore session | Correct protected-page access | Pass | Pending deployment |
| UAT-04 | Update profile and password | Saved values and authentication remain secure | Pass | Pending deployment |
| UAT-05 | Browse/search/filter/sort products | Only active matching products appear | Pass | Pending deployment |
| UAT-06 | Open active/inactive product | Active opens; inactive returns not found | Pass | Pending deployment |
| UAT-07 | Add/update/remove cart item | Totals and stock limits remain correct | Pass | Pending deployment |
| UAT-08 | Checkout with COD | One order, server total, pending COD state | Pass | Pending deployment |
| UAT-09 | Checkout with bKash | Merchant instructions shown; PIN/OTP never requested | Pass | Pending deployment |
| UAT-10 | Submit valid/duplicate transaction ID | Pending verification; duplicate blocked | Pass | Pending deployment |
| UAT-11 | Admin verifies/rejects bKash | Customer sees updated payment state | Pass | Pending deployment |
| UAT-12 | Cancel eligible order | Order cancelled and stock restored once | Pass | Pending deployment |
| UAT-13 | View another customer's order | Not found/forbidden with no data exposure | Pass | Pending deployment |
| UAT-14 | Admin manages catalogue/content | Add, edit, activate, reorder, and remove work | Pass | Pending deployment |
| UAT-15 | Keyboard-only use | Focus visible; menus/forms/actions reachable | Pass | Pending deployment |
| UAT-16 | Reduced-motion preference | Nonessential transitions/animations disabled | Pass | Pending deployment |
| UAT-17 | Desktop/tablet/mobile layout | No page-level horizontal overflow or clipped actions | Pass | Pending deployment |
| UAT-18 | API/network failure | Loading stops and actionable error is displayed | Pass | Pending deployment |

Final local decision: **Accepted for deployment preparation**. Final production acceptance remains pending until hosting credentials and URLs are supplied.
