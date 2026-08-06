# Sprint 5 UAT and Customer Guide

## Test conditions

- Use a test customer account and products with known stock.
- Configure `VITE_BKASH_MERCHANT_NUMBER` with the NazRiy merchant number.
- Use a bKash transaction created specifically for the test order.
- Never enter or request a customer’s bKash PIN, OTP, or verification code.
- An administrator must compare the transaction ID, amount, and merchant statement before marking payment as Paid.

## Acceptance checklist

| ID | Scenario | Expected result |
| --- | --- | --- |
| UAT-01 | Browse, search, filter, sort, and open a product | Correct products, images, price, options, and stock appear. |
| UAT-02 | Add an option to cart and change quantity | Totals and persistence update without exceeding stock. |
| UAT-03 | Open protected checkout while signed out | Login is required and the intended destination is retained. |
| UAT-04 | Register/login and restore a valid session | Customer returns to checkout without losing the cart. |
| UAT-05 | Select bKash | Merchant number, exact total, safe instructions, and transaction-ID field appear. |
| UAT-06 | Submit an invalid transaction ID | Accessible validation prevents order submission. |
| UAT-07 | Submit a valid unused transaction ID | One order is created, stock decreases once, and payment becomes Pending verification. |
| UAT-08 | Submit the same transaction ID on another order | Backend rejects the duplicate reference. |
| UAT-09 | Administrator verifies the reference | Payment becomes Paid and the customer sees the verified transaction ID. |
| UAT-10 | Administrator rejects the reference | Payment becomes Failed with a clear customer-facing explanation. |
| UAT-11 | Cancel an unverified bKash payment | Payment/order become Cancelled and reserved stock is restored. |
| UAT-12 | Select cash on delivery | Order is confirmed with payment pending until delivery. |
| UAT-13 | Open another customer’s order/payment endpoint | Access is denied without exposing the order. |
| UAT-14 | Test keyboard, screen reader, reduced motion, tablet, and mobile layouts | Focus, labels, announcements, and layout remain usable. |

## Customer bKash instructions

1. Add products to the cart and continue to checkout.
2. Enter delivery information and select **bKash**.
3. Open the bKash app and choose **Send Money**.
4. Send the exact checkout total to the displayed NazRiy merchant number.
5. Copy the transaction ID from the bKash confirmation message.
6. Enter the transaction ID and place the order.
7. The order shows **Pending** until NazRiy verifies the payment.
8. Track the order from **Account → Orders**.

## Administrator verification

1. Open **Administration → Payments**.
2. Filter by method **bKash** and status **Pending**.
3. Compare the submitted transaction ID, amount, date, and merchant statement.
4. Select verified records and run **Verify selected bKash payments**.
5. Select invalid records and run **Reject selected bKash payments**.
6. Never approve a payment from a screenshot alone; verify it against the merchant account.

## Evidence record

For each UAT run, record tester, date, device/browser, order ID, transaction ID with sensitive portions masked, expected result, actual result, screenshot filename, issue ID, retest result, and approver.
