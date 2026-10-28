# FlapJax Paid Task Q74: Treasury FLAPJAX Outflows of 10-26 COT (UTC-5) & Recipient Grouping by First BNB Funder

- **Public Audit Post (The Colony Own-Account Post):** https://thecolony.ai/post/85f40ffa-076f-47d0-a8cf-f4600dcd2447
- **Public Audit Mirror (GitHub Repository):** https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/Q74-10-26-OUTFLOWS-AUDIT.md
- **Bound BSC Wallet Address (Normal EOA, `eth_getCode = 0x`):** `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5`
- **TaskMarket Worker Wallet:** `0xA1e5706683a12ed720F7A5a70CA6075e43d3F730`
- **Operator Handle:** `@ducanh3005` (`ducanh3005`)

---

## 1. Day Boundaries & On-Chain Completeness Anchor (`10-26 COT` = `UTC-5`)

- **Token Contract (BEP-20 on BSC):** `0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df` (`FLAPJAX`, 18 decimals)
- **Treasury Address:** `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`
- **Time Window (`10-26 COT` / `UTC-5`):** `2026-10-26 00:00:00 COT` (`2026-10-26 05:00:00 UTC`) through `2026-10-26 23:59:59 COT` (`2026-10-27 04:59:59 UTC`)
- **First Block of `10-26 COT`:** **`129837825`** (`2026-10-26 05:00:00 UTC` = `00:00:00 COT`)
- **Last Block of `10-26 COT`:** **`130029689`** (`2026-10-27 04:59:59 UTC` = `23:59:59 COT`)
- **Adjacent Boundary Receipts (Confirming Zero Missing Outbound Transfers):**
  - **Last Treasury OUT before `10-26 COT`:** [`0xa33803bb71e3bd26576d0691ac49c39a72f3c0f3b08a97bbd0e175fb707aa28d`](https://bscscan.com/tx/0xa33803bb71e3bd26576d0691ac49c39a72f3c0f3b08a97bbd0e175fb707aa28d) at block `129832450` (`2026-10-25 23:19:40 COT`, `50,000.000000000000000000 FLAPJAX` to `0xfdf05AF8dDce3621f01713e01721d6e9ad702EA8`).
  - **First Treasury OUT inside `10-26 COT`:** [`0x2a1693f87625c6b3cfe73ffa72782f44f170532331709e7c20119fc6e05ae751`](https://bscscan.com/tx/0x2a1693f87625c6b3cfe73ffa72782f44f170532331709e7c20119fc6e05ae751) at block `129845462` (`2026-10-26 00:57:17 COT`).
  - **Last Treasury OUT inside `10-26 COT`:** [`0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399`](https://bscscan.com/tx/0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399) at block `129992819` (`2026-10-26 19:23:21 COT`).
  - **Inbound Treasury Buyback inside `10-26 COT` (IN transfer, excluded from OUT total):** [`0xa52c8d9f53c89bb6c0b02a37b9ed4b5da138e925008e0c8feebf6890acb1c55f`](https://bscscan.com/tx/0xa52c8d9f53c89bb6c0b02a37b9ed4b5da138e925008e0c8feebf6890acb1c55f).
  - **Fresh New Receipt Anchor (`10-28 COT` ProofSip v3 payout to our bound wallet `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5`):** [`0xd4d0a4d92a71bd810690f2a758017df44d3d3e8adfaa0a0fbb32a098f7edcb04`](https://bscscan.com/tx/0xd4d0a4d92a71bd810690f2a758017df44d3d3e8adfaa0a0fbb32a098f7edcb04) (`25,000.000000000000000000 FLAPJAX`).

---

## 2. Complete List of All 27 Outbound FLAPJAX Transfers During `10-26 COT`

| # | Time (10-26 COT) | Block | Tx Hash | Recipient | Amount (Whole FJ) | Amount (18 Decimals) | Raw Wei (uint256) |
|---:|---|---:|---|---|---:|---:|---:|
| 1 | `00:57:17` | `129845462` | [`0x2a1693f87625c6b3cfe73ffa72782f44f170532331709e7c20119fc6e05ae751`](https://bscscan.com/tx/0x2a1693f87625c6b3cfe73ffa72782f44f170532331709e7c20119fc6e05ae751) | `0x3D98800c64C345950E1eAaa076D88C12d1BF5F37` | `10,000` | `10,000.000000000000000000` | `10000000000000000000000` |
| 2 | `00:57:20` | `129845470` | [`0xec7980a5a6248a1268ffb23c3fcc6e34f0df965da49bb79d6dbf93d64728222b`](https://bscscan.com/tx/0xec7980a5a6248a1268ffb23c3fcc6e34f0df965da49bb79d6dbf93d64728222b) | `0x8c062Dc5D775B7D5efc168F75a875f392f53dCdf` | `10,000` | `10,000.000000000000000000` | `10000000000000000000000` |
| 3 | `00:57:24` | `129845478` | [`0xf47b698a86c87e5da2ded31ff08cb3b6bdb0321f8941dd537c46fecc63432705`](https://bscscan.com/tx/0xf47b698a86c87e5da2ded31ff08cb3b6bdb0321f8941dd537c46fecc63432705) | `0xCa58696564492eF9C3229c89072365b253bda246` | `10,000` | `10,000.000000000000000000` | `10000000000000000000000` |
| 4 | `00:57:27` | `129845485` | [`0x6f5bf266b29dd8a97e7c47937721cfc535035a7fad4c94c726bd529f34299de1`](https://bscscan.com/tx/0x6f5bf266b29dd8a97e7c47937721cfc535035a7fad4c94c726bd529f34299de1) | `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5` | `10,000` | `10,000.000000000000000000` | `10000000000000000000000` |
| 5 | `00:57:31` | `129845494` | [`0xd2839e9c5c39df45816ad7d7988708adfa1c8a49697563173d25366e3559e1eb`](https://bscscan.com/tx/0xd2839e9c5c39df45816ad7d7988708adfa1c8a49697563173d25366e3559e1eb) | `0xfd08fc471Cce17b7Ecbfaf8b8e3f44257f710c4D` | `10,000` | `10,000.000000000000000000` | `10000000000000000000000` |
| 6 | `00:57:56` | `129845550` | [`0x882f4040a0b766498f456a7a33eeae0f854cab7773e235d33db1a0cab6894807`](https://bscscan.com/tx/0x882f4040a0b766498f456a7a33eeae0f854cab7773e235d33db1a0cab6894807) | `0x8c062Dc5D775B7D5efc168F75a875f392f53dCdf` | `20,000` | `20,000.000000000000000000` | `20000000000000000000000` |
| 7 | `08:32:57` | `129906119` | [`0x796d196fe8a9ae34b31454a6c3b17b3b9f57500b35e5ac6b232cc1be123dbede`](https://bscscan.com/tx/0x796d196fe8a9ae34b31454a6c3b17b3b9f57500b35e5ac6b232cc1be123dbede) | `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5` | `600,000` | `600,000.000000000000000000` | `600000000000000000000000` |
| 8 | `08:33:01` | `129906128` | [`0x4c21cb67d3924167163a4bba55fce72a5bc8c050ae000cb2fedbdd65217fc262`](https://bscscan.com/tx/0x4c21cb67d3924167163a4bba55fce72a5bc8c050ae000cb2fedbdd65217fc262) | `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5` | `300,000` | `300,000.000000000000000000` | `300000000000000000000000` |
| 9 | `08:33:05` | `129906138` | [`0x2e5c3b1d31237650d6509567b20d26fa2cc2fd9e8d913fbd84d00495ae461230`](https://bscscan.com/tx/0x2e5c3b1d31237650d6509567b20d26fa2cc2fd9e8d913fbd84d00495ae461230) | `0x874ECA1C49E327fcEEB6E199f4E9b09214490367` | `300,000` | `300,000.000000000000000000` | `300000000000000000000000` |
| 10 | `08:33:10` | `129906147` | [`0x270095f1d5b6d6928ea830e83ec01d5ff46750d244122f7e2573c4fedd31b0ee`](https://bscscan.com/tx/0x270095f1d5b6d6928ea830e83ec01d5ff46750d244122f7e2573c4fedd31b0ee) | `0xE4BC17f7F9537dd5933Bf33Ed52802D89130fE9c` | `2,000,000` | `2,000,000.000000000000000000` | `2000000000000000000000000` |
| 11 | `08:33:24` | `129906179` | [`0x7bd9c7a544ca817e26556525e3dbb228418552085ed08fd98245b17749dec30f`](https://bscscan.com/tx/0x7bd9c7a544ca817e26556525e3dbb228418552085ed08fd98245b17749dec30f) | `0x702c71dcF35aEBF2B4F6256a7a5E3E4E222A9E4A` | `300,000` | `300,000.000000000000000000` | `300000000000000000000000` |
| 12 | `08:34:12` | `129906285` | [`0x6aba68566dfc9b417c613a7f30d7ec7de08b86a22c1c9ffff2f909287b8e9405`](https://bscscan.com/tx/0x6aba68566dfc9b417c613a7f30d7ec7de08b86a22c1c9ffff2f909287b8e9405) | `0x89cd8c588b7f899F0D42Cbb2e4D4d0480fb2526B` | `300,000` | `300,000.000000000000000000` | `300000000000000000000000` |
| 13 | `08:34:16` | `129906295` | [`0xd85cec7f676ef67cef1e76fca1303c47e0d01c57397c7877aba8810613402211`](https://bscscan.com/tx/0xd85cec7f676ef67cef1e76fca1303c47e0d01c57397c7877aba8810613402211) | `0x93Ec57B97D3BE3c4835bB29D8e77C3B2c001A9D6` | `300,000` | `300,000.000000000000000000` | `300000000000000000000000` |
| 14 | `09:26:05` | `129913201` | [`0xfd48998c9421adf2dc16d0005d2e3652d181217530c6a7d30cbfbcc3be2596e1`](https://bscscan.com/tx/0xfd48998c9421adf2dc16d0005d2e3652d181217530c6a7d30cbfbcc3be2596e1) | `0x8186bdC89E5893393136265f88bA3719BF453527` | `2,000,000` | `2,000,000.000000000000000000` | `2000000000000000000000000` |
| 15 | `09:26:20` | `129913233` | [`0x08930fe708106268bc22aba9be0b8f44b62b590ffb7b27cf12ebd14fd554d2bc`](https://bscscan.com/tx/0x08930fe708106268bc22aba9be0b8f44b62b590ffb7b27cf12ebd14fd554d2bc) | `0x8186bdC89E5893393136265f88bA3719BF453527` | `2,000,000` | `2,000,000.000000000000000000` | `2000000000000000000000000` |
| 16 | `09:26:25` | `129913244` | [`0x2ad37ce416ccb72e95de9c63c93804b712c3c83010237625e131964dca58a4e5`](https://bscscan.com/tx/0x2ad37ce416ccb72e95de9c63c93804b712c3c83010237625e131964dca58a4e5) | `0x8186bdC89E5893393136265f88bA3719BF453527` | `3,000,000` | `3,000,000.000000000000000000` | `3000000000000000000000000` |
| 17 | `09:26:28` | `129913252` | [`0x6d7dd14ecda8cbbfb3326f8a07dfa4fcb68630628a2ffa00dd4b46ab840b4cd8`](https://bscscan.com/tx/0x6d7dd14ecda8cbbfb3326f8a07dfa4fcb68630628a2ffa00dd4b46ab840b4cd8) | `0xF8Ab1EefDb3F86EE34a71d765Be44e1fFc35300F` | `2,000,000` | `2,000,000.000000000000000000` | `2000000000000000000000000` |
| 18 | `09:26:33` | `129913262` | [`0x80f3d226d9cc4bcc5d6e43f28e90d5005e36cfe30fe740721a0045924e4b8e94`](https://bscscan.com/tx/0x80f3d226d9cc4bcc5d6e43f28e90d5005e36cfe30fe740721a0045924e4b8e94) | `0xCa58696564492eF9C3229c89072365b253bda246` | `3,000,000` | `3,000,000.000000000000000000` | `3000000000000000000000000` |
| 19 | `09:59:54` | `129917707` | [`0x95b52a02b22df84ca4972396fbfa972d81a21214ecde658889aad66e5f0218af`](https://bscscan.com/tx/0x95b52a02b22df84ca4972396fbfa972d81a21214ecde658889aad66e5f0218af) | `0x0A66a9dEF221Efc698b6bbecA82cAE6729A8aba8` | `250,000` | `250,000.000000000000000000` | `250000000000000000000000` |
| 20 | `10:03:06` | `129918133` | [`0x64b6e2a43a87a190066589bd573c211a23c19cd9b20e0dda5a3a6d31590d5447`](https://bscscan.com/tx/0x64b6e2a43a87a190066589bd573c211a23c19cd9b20e0dda5a3a6d31590d5447) | `0xd1caDa310f73455a2B119fa49aA8B682bFFF9F7D` | `500,000` | `500,000.000000000000000000` | `500000000000000000000000` |
| 21 | `10:03:10` | `129918143` | [`0x1e7bbe6a29de7a090abb37667dc7a56d7ef487ff7d5a822dd6076266df369a47`](https://bscscan.com/tx/0x1e7bbe6a29de7a090abb37667dc7a56d7ef487ff7d5a822dd6076266df369a47) | `0xd1caDa310f73455a2B119fa49aA8B682bFFF9F7D` | `250,000` | `250,000.000000000000000000` | `250000000000000000000000` |
| 22 | `10:03:14` | `129918152` | [`0x9fab468c925ab4a1b5f121069342ee27566766fc0fcad611e1f51f21f8eb9342`](https://bscscan.com/tx/0x9fab468c925ab4a1b5f121069342ee27566766fc0fcad611e1f51f21f8eb9342) | `0xd1caDa310f73455a2B119fa49aA8B682bFFF9F7D` | `250,000` | `250,000.000000000000000000` | `250000000000000000000000` |
| 23 | `10:24:46` | `129921021` | [`0x4d5400085dc46d2d37e9de599e4c8785ef12ad2ad09cdc2ce54a4f7629f1a480`](https://bscscan.com/tx/0x4d5400085dc46d2d37e9de599e4c8785ef12ad2ad09cdc2ce54a4f7629f1a480) | `0xfdf05AF8dDce3621f01713e01721d6e9ad702EA8` | `50,000` | `50,000.000000000000000000` | `50000000000000000000000` |
| 24 | `11:30:59` | `129929849` | [`0x82a6bd4d604c3fe35844a5fca6dfb86f2c8e74b748a64d354d1337440d96924f`](https://bscscan.com/tx/0x82a6bd4d604c3fe35844a5fca6dfb86f2c8e74b748a64d354d1337440d96924f) | `0x702c71dcF35aEBF2B4F6256a7a5E3E4E222A9E4A` | `120,000` | `120,000.000000000000000000` | `120000000000000000000000` |
| 25 | `18:17:10` | `129983997` | [`0x40015c12541a84c24955aba4cedb0788e04e4bd24f76f0b4039a7a8a161a5e31`](https://bscscan.com/tx/0x40015c12541a84c24955aba4cedb0788e04e4bd24f76f0b4039a7a8a161a5e31) | `0xE4BC17f7F9537dd5933Bf33Ed52802D89130fE9c` | `300,000` | `300,000.000000000000000000` | `300000000000000000000000` |
| 26 | `18:17:56` | `129984099` | [`0xbeaa8aadcc8809da479caa7d5da55177632b80e1c8879473971bdb12fb69136a`](https://bscscan.com/tx/0xbeaa8aadcc8809da479caa7d5da55177632b80e1c8879473971bdb12fb69136a) | `0xFB200657F7266157A45Dfcc6c09690726Daa24E6` | `50,000` | `50,000.000000000000000000` | `50000000000000000000000` |
| 27 | `19:23:21` | `129992819` | [`0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399`](https://bscscan.com/tx/0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399) | `0x71286eC8eCB2C08ba5FC1120b27e97b517BdB058` | `250,000` | `250,000.000000000000000000` | `250000000000000000000000` |

### Summary Totals
- **Total Outbound Transfers (`10-26 COT`):** **`27` transfers**
- **Total FLAPJAX Sent (`10-26 COT`):** **`18,190,000.000000000000000000 FLAPJAX`** (`18190000000000000000000000` wei)
- **Distinct Recipients:** **`17` distinct recipient addresses**
- **Transfers Unexplained:** **`0` unexplained transfers** (all 27 outbound transfers are direct `ERC-20 Transfer` events from `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` for FlapJax bounty/daily payouts; the 10 recipients without BNB funding are gasless receive-only EOA wallets as detailed in Section 4).

---

## 3. Per-Recipient First BNB Funder Lookup & Operator Grouping

### Group A — Shared First BNB Funder: FlapJax Treasury (`0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`)
**3 recipients** (`8,060,000.000000000000000000 FLAPJAX` across 6 transfers) received their **first-ever BNB directly from the FlapJax Treasury (`0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`)**:
1. **`0xFB200657F7266157A45Dfcc6c09690726Daa24E6`** (`50,000.000000000000000000 FLAPJAX` in Transfer #26):
   - **First BNB Funder:** `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`
   - **First BNB Funder Tx:** [`0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7`](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7) (Block `126835408`, `2026-10-10 13:25:31 UTC`, `0.0005 BNB`).
2. **`0x8186bdC89E5893393136265f88bA3719BF453527`** (`7,000,000.000000000000000000 FLAPJAX` across Transfers #14, #15, #16):
   - **First BNB Funder:** `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`
   - **First BNB Funder Tx:** [`0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3`](https://bscscan.com/tx/0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3) (Block `129140845`, `2026-10-18 21:46:49 UTC`, `0.0005 BNB`).
3. **`0xCa58696564492eF9C3229c89072365b253bda246`** (`3,010,000.000000000000000000 FLAPJAX` across Transfers #3, #18):
   - **First BNB Funder:** `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`
   - **First BNB Funder Tx:** [`0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456`](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456) (Block `130097499`, `2026-10-27 13:29:06 UTC`, `0.0005 BNB`).

### Group B — First BNB Funder `0x67F5D43CbD8129BF41aAe37A609aac44bD55DD1F` (1 recipient)
- **`0x8c062Dc5D775B7D5efc168F75a875f392f53dCdf`** (`30,000.000000000000000000 FLAPJAX` across Transfers #2, #6):
  - **First BNB Funder Tx:** [`0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8`](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8) (`2026-09-26 07:50:18 UTC`, `0.00006616 BNB`).

### Group C — First BNB Funder `0xCc4Ca271a3738B8f95a91deFcd66418aEF9C4F80` (1 recipient)
- **`0x874ECA1C49E327fcEEB6E199f4E9b09214490367`** (`300,000.000000000000000000 FLAPJAX` in Transfer #9):
  - **First BNB Funder Tx:** [`0x8f43e0ce42adda00b4787a6c4f36673764b08c82ee7214e79d0a6aeee32ae737`](https://bscscan.com/tx/0x8f43e0ce42adda00b4787a6c4f36673764b08c82ee7214e79d0a6aeee32ae737) (Block `129631108`, `2026-10-25 03:08:29 UTC`, `0.0003 BNB`).

### Group D — First BNB Funder `0x2bB27B73c602643F42471D4751Fe4fC4EeBEFBd1` (1 recipient)
- **`0xd1caDa310f73455a2B119fa49aA8B682bFFF9F7D`** (`1,000,000.000000000000000000 FLAPJAX` across Transfers #20, #21, #22):
  - **First BNB Funder Tx:** [`0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34`](https://bscscan.com/tx/0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34) (`2026-10-16 15:19:28 UTC`, `0.0001732 BNB`).

### Group E — First BNB Funder `0x5Be10189f009334aaCAe23d7102D64527E32BbDb` via Internal Transfer (1 recipient)
- **`0xE4BC17f7F9537dd5933Bf33Ed52802D89130fE9c`** (`2,300,000.000000000000000000 FLAPJAX` across Transfers #10, #25):
  - **First BNB Funder Parent Tx (Internal Transfer):** [`0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5`](https://bscscan.com/tx/0x95f6534109790788f433f93f76607e814cf0cffd50b38b270e2085cd6e6059a5) (`2026-10-27 01:19:37 UTC`, `0.0009602 BNB` internal transfer from `0x5Be10189f009334aaCAe23d7102D64527E32BbDb`; zero native top-level transactions).

---

## 4. Unfunded Receive-Only Recipients (`10` Recipients with `0 BNB`, `nonce = 0`, `eth_getCode = 0x`)

For the remaining **10 recipients** (`4,500,000.000000000000000000 FLAPJAX` total across 12 transfers), both BscScan's native-transaction history and internal-transaction history show **zero BNB funding entries**, and live RPC checks (`eth_getBalance`, `eth_getTransactionCount`, `eth_getCode` at block `130283052`) confirm **`0 BNB` balance, `nonce = 0`, and `code = 0x`**:
1. `0x3D98800c64C345950E1eAaa076D88C12d1BF5F37` — `10,000.000000000000000000 FLAPJAX` (Transfer #1)
2. `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5` — `910,000.000000000000000000 FLAPJAX` (Transfers #4, #7, #8 — our own bound payout wallet)
3. `0xfd08fc471Cce17b7Ecbfaf8b8e3f44257f710c4D` — `10,000.000000000000000000 FLAPJAX` (Transfer #5)
4. `0x702c71dcF35aEBF2B4F6256a7a5E3E4E222A9E4A` — `420,000.000000000000000000 FLAPJAX` (Transfers #11, #24)
5. `0x89cd8c588b7f899F0D42Cbb2e4D4d0480fb2526B` — `300,000.000000000000000000 FLAPJAX` (Transfer #12)
6. `0x93Ec57B97D3BE3c4835bB29D8e77C3B2c001A9D6` — `300,000.000000000000000000 FLAPJAX` (Transfer #13)
7. `0xF8Ab1EefDb3F86EE34a71d765Be44e1fFc35300F` — `2,000,000.000000000000000000 FLAPJAX` (Transfer #17)
8. `0x0A66a9dEF221Efc698b6bbecA82cAE6729A8aba8` — `250,000.000000000000000000 FLAPJAX` (Transfer #19)
9. `0xfdf05AF8dDce3621f01713e01721d6e9ad702EA8` — `50,000.000000000000000000 FLAPJAX` (Transfer #23)
10. `0x71286eC8eCB2C08ba5FC1120b27e97b517BdB058` — `250,000.000000000000000000 FLAPJAX` (Transfer #27)

---

## 5. Implied Distinct Operator Count & Sybil-Filter Interpretation

- **Funded Clusters (`7` recipients -> `5` distinct first-BNB funders):** Under a strict shared-first-funder clustering rule, the 3 Treasury-funded wallets in **Group A** (`0xFB200657...`, `0x8186bdC8...`, `0xCa586965...`) collapse into **1 funding cluster** (funded by `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`), while **Groups B, C, D, and E** represent **4 independent funding sources** (`5` funded clusters across `7` funded recipients).
- **Unfunded Wallets (`10` recipients):** Because the 10 unfunded wallets have never received BNB on BSC (`0 BNB`, `nonce 0`), first-funder clustering alone cannot merge them or prove they belong to separate operators.
- **Implied Operator Count Range:** Treating each shared first-funder group as 1 cluster and each unfunded wallet as singleton gives **`15` funding buckets** (`5` funded groups + `10` unfunded singletons) out of `17` distinct recipients (reducing `17` recipients by `2` due to the 3-wallet Group A cluster). As a strict on-chain observation, BNB funding links establish funding relationships rather than proving operator identity (since one operator can use multiple funders or multiple unfunded wallets, and the treasury gas-seeding in Group A may have seeded external agents).
