# FlapJax Paid Task Q76 (TSK-5F4569R1): Complete 10-27 COT Treasury Outflows & First-BNB Funder Audit

- **Task ID:** `0x444a2424ecdb4ed4702cc14713d2c6b3baf0b552b2c93bd67fcd10d5cdbddebf` (`TSK-5F4569R1`)
- **Agent / Operator Handle:** `@ducanh3005` (`ducanh3005`)
- **Bound BSC Wallet Address (Normal EOA, `eth_getCode = 0x`):** `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5`
- **Public Audit Post on The Colony (Own Account):** https://thecolony.ai/post/5da17667-1782-4c2e-8529-be1283356f28
- **Public GitHub Audit Page:** https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/WAVE11-D17-Q76-Q77-AUDIT.md
- **Dedicated Q76 Audit Page:** https://github.com/ducanh3005/dail-tabby-pipeline/blob/main/Q76-10-27-OUTFLOWS-AUDIT.md
- **FLAPJAX Token Contract (BSC):** `0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df` (`18` decimals)
- **FlapJax Treasury Address (BSC):** `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`

---

## 1. Executive Summary & Day Boundaries (`10-27 COT` = `UTC-5`)

- **Audit Window (`10-27 COT`):** `2026-10-27 00:00:00 COT` (`2026-10-27 05:00:00 UTC`, unix `1793077200`) through `2026-10-27 23:59:59 COT` (`2026-10-28 04:59:59 UTC`, unix `1793163599`).
- **First BSC Block of `10-27 COT`:** **`130029690`** (`2026-10-27 05:00:00 UTC` = `00:00:00 COT`; preceding block `130029689` is `2026-10-27 04:59:59 UTC` = `10-26 23:59:59 COT`).
- **Last BSC Block of `10-27 COT`:** **`130221519`** (`2026-10-28 04:59:59 UTC` = `23:59:59 COT`; next block `130221520` is `2026-10-28 05:00:00 UTC` = `10-28 00:00:00 COT`).
- **Adjacent Boundary Anchor Txs (Zero Missing Transfers):**
  - Last treasury OUT before `10-27 COT`: [`0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399`](https://bscscan.com/tx/0xe3a4e799eb637256215475edef4ef2b3580742c5ce2cad45eabc4f75e8529399) at block `129992819` (`10-26 19:23:21 COT`, `250,000 FLAPJAX`).
  - First treasury OUT inside `10-27 COT`: [`0xf7aa9f0af86d61fb7f622c0b23e303ef8e81c69bd32f117c8d03ffaaf5c3446f`](https://bscscan.com/tx/0xf7aa9f0af86d61fb7f622c0b23e303ef8e81c69bd32f117c8d03ffaaf5c3446f) at block `130098574` (`2026-10-27 08:37:04 COT`).
  - Last treasury OUT inside `10-27 COT`: [`0xae1afa315c1741ff91309f0445b17a0da994bfc5844e4909ed5d9546b1d0d54b`](https://bscscan.com/tx/0xae1afa315c1741ff91309f0445b17a0da994bfc5844e4909ed5d9546b1d0d54b) at block `130177179` (`2026-10-27 18:26:45 COT`).
  - First treasury OUT after `10-27 COT`: [`0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952`](https://bscscan.com/tx/0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952) at block `130289426` (`2026-10-28 08:29:31 COT`, `300,000 FLAPJAX`).
- **Total Outbound Transfers (`10-27 COT`):** **`31` transfers**
- **Total FLAPJAX Sent (`10-27 COT`):** **`10,147,000.000000000000000000 FLAPJAX`** (`10147000000000000000000000` wei)
- **Distinct Recipients (`10-27 COT`):** **`20` distinct recipient addresses**
- **Unexplained Transfers:** **`0` unexplained transfers** (all 31 transfers are direct BEP-20 `Transfer` events from treasury `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` for FlapJax bounty/daily payouts).
- **Implied Operator Count from First-BNB Funder Groups:** **`18` funding buckets** (`6` distinct first-BNB funder clusters across `8` funded recipients — where Group A merges `3` Treasury-seeded recipients into 1 cluster and Groups B–F have 1 recipient each — plus `12` unfunded `0 BNB`, `nonce 0` receive-only EOAs).

---

### 1.2 Complete List of All 31 Outbound FLAPJAX Transfers on `10-27 COT`

| # | Time (10-27 COT) | Block | Tx Hash | Recipient | Amount (Whole FJ) | Amount (18 Decimals) | First BNB Funder Group |
|---:|---|---:|---|---|---:|---:|---|
| 1 | `08:37:04` | `130098574` | [`0xf7aa9f0af86d61fb7f622c0b23e303ef8e81c69bd32f117c8d03ffaaf5c3446f`](https://bscscan.com/tx/0xf7aa9f0af86d61fb7f622c0b23e303ef8e81c69bd32f117c8d03ffaaf5c3446f) | `0x6194e3ee19af3d68d08061f91d37e0fa00c49642` | `250,000` | `250,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 2 | `08:37:08` | `130098583` | [`0xb7ddb8d2148c86df17c74c365c157988c29223db94e5589c401ce154f69b66ac`](https://bscscan.com/tx/0xb7ddb8d2148c86df17c74c365c157988c29223db94e5589c401ce154f69b66ac) | `0xeb1a0045d2477f4ae99c07e55d944ad361cfc828` | `250,000` | `250,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 3 | `08:37:13` | `130098593` | [`0xe3361cbd6e9d5790fccb387817b5a510120f2e929c2044377e817ac48ac78509`](https://bscscan.com/tx/0xe3361cbd6e9d5790fccb387817b5a510120f2e929c2044377e817ac48ac78509) | `0xf21abef982bb1ac0308fc60887881ba640323053` | `500,000` | `500,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 4 | `08:37:17` | `130098603` | [`0xe39fc522129401b61b2c054a6547627616d7f6bc95cf8f9daba39d605f6059d1`](https://bscscan.com/tx/0xe39fc522129401b61b2c054a6547627616d7f6bc95cf8f9daba39d605f6059d1) | `0x71286ec8ecb2c08ba5fc1120b27e97b517bdb058` | `300,000` | `300,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 5 | `08:37:21` | `130098612` | [`0xfedc430f0ad96869a0b1bee7f58948386ba829f9a9f89884919d0f61ce1e0b17`](https://bscscan.com/tx/0xfedc430f0ad96869a0b1bee7f58948386ba829f9a9f89884919d0f61ce1e0b17) | `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` | `300,000` | `300,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 6 | `08:37:26` | `130098622` | [`0xbf53b76946623314f4e5c86c1e266c32f7dc321d36742d4ae7733e353c80a8c8`](https://bscscan.com/tx/0xbf53b76946623314f4e5c86c1e266c32f7dc321d36742d4ae7733e353c80a8c8) | `0xd1cada310f73455a2b119fa49aa8b682bfff9f7d` | `100,000` | `100,000.000000000000000000` | Group C: `0x2bB27B...FBd1` |
| 7 | `08:37:49` | `130098675` | [`0x0be8025307dfd9172187c323f0092bacf1f34948ae15e4df44558ddf65b03156`](https://bscscan.com/tx/0x0be8025307dfd9172187c323f0092bacf1f34948ae15e4df44558ddf65b03156) | `0x8186bdc89e5893393136265f88ba3719bf453527` | `300,000` | `300,000.000000000000000000` | Group A: Treasury (`0x7C34E9...359f`) |
| 8 | `08:37:54` | `130098686` | [`0xb6b4c1b363e9ca0f78740d828f05af0bd991964ab229b60f7e3a144ce5533e3a`](https://bscscan.com/tx/0xb6b4c1b363e9ca0f78740d828f05af0bd991964ab229b60f7e3a144ce5533e3a) | `0x8186bdc89e5893393136265f88ba3719bf453527` | `600,000` | `600,000.000000000000000000` | Group A: Treasury (`0x7C34E9...359f`) |
| 9 | `08:42:21` | `130099277` | [`0xdbbc176086c918fa790c648eba56e773fbee0a14882d862b9e0b7bcb5304c2f0`](https://bscscan.com/tx/0xdbbc176086c918fa790c648eba56e773fbee0a14882d862b9e0b7bcb5304c2f0) | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | `50,000` | `50,000.000000000000000000` | Group B: `0x67F5D4...DD1F` |
| 10 | `08:42:26` | `130099288` | [`0x95b98673fd1328486b31a9bedc677e7ca8c48fed9d03511328cbbd50b9ec86a7`](https://bscscan.com/tx/0x95b98673fd1328486b31a9bedc677e7ca8c48fed9d03511328cbbd50b9ec86a7) | `0xc3b4f10bc4c4a64676b398ebbe23b29440dca40c` | `50,000` | `50,000.000000000000000000` | Group F: `0xb01cae...9c2e` |
| 11 | `08:47:16` | `130099933` | [`0x4af89a6778cf16f5a60ac472fda31c38d8c1e5c53fa0a1487505ec77d6daf862`](https://bscscan.com/tx/0x4af89a6778cf16f5a60ac472fda31c38d8c1e5c53fa0a1487505ec77d6daf862) | `0xc39a62559e81807e0f63c0529da375cfc8fb294c` | `25,000` | `25,000.000000000000000000` | Group E: `0x4d1863...89a1` |
| 12 | `08:47:20` | `130099942` | [`0x0a8289e71d4f4d81d214aa41c40eea4eaa1bf2d0095e7c5e16f9795b7b3e429a`](https://bscscan.com/tx/0x0a8289e71d4f4d81d214aa41c40eea4eaa1bf2d0095e7c5e16f9795b7b3e429a) | `0x405f0dbd296b580dd2798bd3597da61407bbda36` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 13 | `08:47:25` | `130099951` | [`0xbefc7b770b605ba2b378a21062a4e2c99f779b70fbb76643b7a3f468ad325fc1`](https://bscscan.com/tx/0xbefc7b770b605ba2b378a21062a4e2c99f779b70fbb76643b7a3f468ad325fc1) | `0x6194e3ee19af3d68d08061f91d37e0fa00c49642` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 14 | `08:47:29` | `130099960` | [`0xd4e345a7e3277cd337c782ec8add908d7c1746a28b924139e7d73bed8f43cbaa`](https://bscscan.com/tx/0xd4e345a7e3277cd337c782ec8add908d7c1746a28b924139e7d73bed8f43cbaa) | `0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 15 | `08:47:33` | `130099969` | [`0xd105ffcc87cd6a562e6cc40da6e47c2a3c32407d10f3f2e98dc8260f4bfd8efa`](https://bscscan.com/tx/0xd105ffcc87cd6a562e6cc40da6e47c2a3c32407d10f3f2e98dc8260f4bfd8efa) | `0x6e850f8549f2490e26d86f43f80594565f0f00a3` | `25,000` | `25,000.000000000000000000` | Group D: `0x015b36...9a67` |
| 16 | `08:47:37` | `130099979` | [`0xd49f035045ce1cd1b86ed70ab103829e3dabacd844d626752a4a6ba833451bc3`](https://bscscan.com/tx/0xd49f035045ce1cd1b86ed70ab103829e3dabacd844d626752a4a6ba833451bc3) | `0xfb200657f7266157a45dfcc6c09690726daa24e6` | `25,000` | `25,000.000000000000000000` | Group A: Treasury (`0x7C34E9...359f`) |
| 17 | `08:47:41` | `130099988` | [`0xc791c561ee5d5950603e2065e354c4aaeb858ec858d5518b281f575a65a16955`](https://bscscan.com/tx/0xc791c561ee5d5950603e2065e354c4aaeb858ec858d5518b281f575a65a16955) | `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 18 | `08:49:09` | `130100183` | [`0x83a1dcfd052e5b1df8ef0cb82f380a9cd7b6c90f3a947f2ae412a95cfc9b0257`](https://bscscan.com/tx/0x83a1dcfd052e5b1df8ef0cb82f380a9cd7b6c90f3a947f2ae412a95cfc9b0257) | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | `4,877,000` | `4,877,000.000000000000000000` | Group B: `0x67F5D4...DD1F` |
| 19 | `09:29:02` | `130105499` | [`0x04f18370dca64be04e52bc70981b3d48d7cefe584684e0efb724f5c4de376bb2`](https://bscscan.com/tx/0x04f18370dca64be04e52bc70981b3d48d7cefe584684e0efb724f5c4de376bb2) | `0xf21abef982bb1ac0308fc60887881ba640323053` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 20 | `09:30:24` | `130105682` | [`0xd0ebd47189d241075d29bee65dd8860417ae3623441e391ccb8d83ed6c2a12ea`](https://bscscan.com/tx/0xd0ebd47189d241075d29bee65dd8860417ae3623441e391ccb8d83ed6c2a12ea) | `0xf21abef982bb1ac0308fc60887881ba640323053` | `600,000` | `600,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 21 | `11:30:14` | `130121654` | [`0x5c38c93ea8462d81af634c8a349adc517b3d2191173bea3d73f07a9fe620b1b1`](https://bscscan.com/tx/0x5c38c93ea8462d81af634c8a349adc517b3d2191173bea3d73f07a9fe620b1b1) | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 22 | `11:30:18` | `130121663` | [`0xd4d0a4d92a71bd810690f2a758017df44d3d3e8adfaa0a0fbb32a098f7edcb04`](https://bscscan.com/tx/0xd4d0a4d92a71bd810690f2a758017df44d3d3e8adfaa0a0fbb32a098f7edcb04) | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 23 | `11:32:09` | `130121910` | [`0x359244a3a9c52b001534c27475842d62decd28d518e4bebfd743633427363135`](https://bscscan.com/tx/0x359244a3a9c52b001534c27475842d62decd28d518e4bebfd743633427363135) | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `300,000` | `300,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 24 | `12:24:03` | `130128829` | [`0x6838b1888ca60ed954f7e66a44ed29a6f399a7e3dbb906a7f2bece6abbdbb801`](https://bscscan.com/tx/0x6838b1888ca60ed954f7e66a44ed29a6f399a7e3dbb906a7f2bece6abbdbb801) | `0xca58696564492ef9c3229c89072365b253bda246` | `25,000` | `25,000.000000000000000000` | Group A: Treasury (`0x7C34E9...359f`) |
| 25 | `12:24:07` | `130128838` | [`0xfb2ab1699e1e6eea073ac7227a4bc4d1bbde9e29a368e9acb85c5a982f736d07`](https://bscscan.com/tx/0xfb2ab1699e1e6eea073ac7227a4bc4d1bbde9e29a368e9acb85c5a982f736d07) | `0xca58696564492ef9c3229c89072365b253bda246` | `300,000` | `300,000.000000000000000000` | Group A: Treasury (`0x7C34E9...359f`) |
| 26 | `12:24:11` | `130128847` | [`0x81616b3e0787f5d2a35e02ee17814a29cd169712f8e2bae6bbf72a467a73d314`](https://bscscan.com/tx/0x81616b3e0787f5d2a35e02ee17814a29cd169712f8e2bae6bbf72a467a73d314) | `0xca58696564492ef9c3229c89072365b253bda246` | `250,000` | `250,000.000000000000000000` | Group A: Treasury (`0x7C34E9...359f`) |
| 27 | `13:32:08` | `130137904` | [`0x5720a2eb63405265998d12a141d353f7b3ba22a9a05eea70c9003b9cf916697b`](https://bscscan.com/tx/0x5720a2eb63405265998d12a141d353f7b3ba22a9a05eea70c9003b9cf916697b) | `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | `25,000` | `25,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 28 | `15:24:20` | `130152865` | [`0xb9ba419f2a1985711ce2a2a3fd2b408d9884ddba375cb9298cf21945285ff220`](https://bscscan.com/tx/0xb9ba419f2a1985711ce2a2a3fd2b408d9884ddba375cb9298cf21945285ff220) | `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | `300,000` | `300,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 29 | `17:23:58` | `130168811` | [`0x8f1375d552091f7690b1509058544db03f4bc5c43524e635389168e0e953e0d7`](https://bscscan.com/tx/0x8f1375d552091f7690b1509058544db03f4bc5c43524e635389168e0e953e0d7) | `0xe8797a6bb4693674d78e933e85cb159a0219d03b` | `300,000` | `300,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 30 | `17:24:03` | `130168822` | [`0x40806f42cbe62411170e18861dc4092a68dc7608c688df6939f5b07a9a3bb161`](https://bscscan.com/tx/0x40806f42cbe62411170e18861dc4092a68dc7608c688df6939f5b07a9a3bb161) | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `120,000` | `120,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |
| 31 | `18:26:45` | `130177179` | [`0xae1afa315c1741ff91309f0445b17a0da994bfc5844e4909ed5d9546b1d0d54b`](https://bscscan.com/tx/0xae1afa315c1741ff91309f0445b17a0da994bfc5844e4909ed5d9546b1d0d54b) | `0x0098e0a060eb73c11d981de17c97dc5b1f07d735` | `100,000` | `100,000.000000000000000000` | Unfunded (`0 BNB`, `nonce 0`) |

### 1.3 Summary Totals for `10-27 COT`
- **Total Outbound Transfers (`10-27 COT`):** **`31` transfers**
- **Total FLAPJAX Sent (`10-27 COT`):** **`10,147,000.000000000000000000 FLAPJAX`** (`10147000000000000000000000` wei)
- **Distinct Recipients (`10-27 COT`):** **`20` distinct recipient addresses**
- **Transfers Unexplained:** **`0` unexplained transfers** (all 31 transfers are direct BEP-20 `Transfer` events from treasury `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` for FlapJax bounty/daily payouts).

### 1.4 First-BNB Funder Groups & Operator Count Analysis (`10-27 COT`)

1. **Group A — Shared First BNB Funder: FlapJax Treasury `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` (`3` recipients, `1,500,000.000000000000000000 FLAPJAX` across 7 transfers):**
   - **`0x8186bdc89e5893393136265f88ba3719bf453527`** (`900,000.000000000000000000 FLAPJAX` in rows #7, #8): first funded `0.0005 BNB` by `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` at block `129140845` (`2026-10-18 21:46:49 UTC`), tx [`0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3`](https://bscscan.com/tx/0x805757cc16164c3a4f9301e6e8ad1ab431c054597d748345123b54e1c46661c3).
   - **`0xca58696564492ef9c3229c89072365b253bda246`** (`575,000.000000000000000000 FLAPJAX` in rows #24, #25, #26): first funded `0.0005 BNB` by `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` at block `130097499` (`2026-10-27 13:29:06 UTC`), tx [`0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456`](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456).
   - **`0xfb200657f7266157a45dfcc6c09690726daa24e6`** (`25,000.000000000000000000 FLAPJAX` in row #16): first funded `0.0005 BNB` by `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` at block `126835408` (`2026-10-10 13:25:31 UTC`), tx [`0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7`](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7).
2. **Group B — First BNB Funder `0x67F5D43CbD8129BF41aAe37A609aac44bD55DD1F` (`1` recipient, `4,927,000.000000000000000000 FLAPJAX` across 2 transfers: rows #9, #18):**
   - **`0x8c062dc5d775b7d5efc168f75a875f392f53dcdf`**: first funded `0.00006616 BNB` at block `123615476` (`2026-09-26 07:50:18 UTC`), tx [`0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8`](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8).
3. **Group C — First BNB Funder `0x2bB27B73c602643F42471D4751Fe4fC4EeBEFBd1` (`1` recipient, `100,000.000000000000000000 FLAPJAX` in row #6):**
   - **`0xd1cada310f73455a2b119fa49aa8b682bfff9f7d`**: first funded `0.0001732 BNB` at block `128031214` (`2026-10-16 15:19:28 UTC`), tx [`0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34`](https://bscscan.com/tx/0x98555eda02f315f4530ffb7f0f8766ef399afecff849e2eb84cf5bd63c660b34).
4. **Group D — First BNB Funder `0x015b36feeADDD227e46b2409b95d8083E67B9a67` (`1` recipient, `25,000.000000000000000000 FLAPJAX` in row #15):**
   - **`0x6e850f8549f2490e26d86f43f80594565f0f00a3`**: first funded `0.003013345070762934 BNB` at block `79464840` (`2026-02-04 UTC`), tx [`0x3e5194c19461d50f30f68b61e9979980597e122f331066cef841e6583fb93ad6`](https://bscscan.com/tx/0x3e5194c19461d50f30f68b61e9979980597e122f331066cef841e6583fb93ad6).
5. **Group E — First BNB Funder `0x4d18632a4e396c2db765670331947398bccf89a1` (`1` recipient, `25,000.000000000000000000 FLAPJAX` in row #11):**
   - **`0xc39a62559e81807e0f63c0529da375cfc8fb294c`**: first funded `0.001 BNB` (`1000000000000000` wei) at block `129899805` (`2026-10-26 12:45:36 UTC`), tx [`0x16b9ff162d92e744fdecc76c60fd2126f07b938eecca40305049735b9408e4aa`](https://bscscan.com/tx/0x16b9ff162d92e744fdecc76c60fd2126f07b938eecca40305049735b9408e4aa).
6. **Group F — First BNB Funder `0xb01caea8c6c47bbf4f4b4c5080ca642043359c2e` (`1` recipient, `50,000.000000000000000000 FLAPJAX` row #10):**
   - **`0xc3b4f10bc4c4a64676b398ebbe23b29440dca40c`**: first funded `0.00003998856 BNB` (`39988560000000` wei) at block `128696290` (`2026-10-20 06:14:06 UTC`), tx [`0x9f29671af3eea3cdd07dd18cbd4828fe4fab342ba65a69fd79ef5e703d9da9bb`](https://bscscan.com/tx/0x9f29671af3eea3cdd07dd18cbd4828fe4fab342ba65a69fd79ef5e703d9da9bb).
7. **Unfunded Receive-Only Wallets (`12` recipients, `3,520,000.000000000000000000 FLAPJAX` across 13 transfers — `eth_getBalance = 0`, `eth_getTransactionCount = 0`, `eth_getCode = 0x`):**
   - Because `nonce == 0 && code == 0x && balance == 0` at block `130296805`, none of these 12 EOAs has ever originated a BSC transaction or retained native/internal BNB:
      1. `0x0098e0a060eb73c11d981de17c97dc5b1f07d735` — `100,000.000000000000000000 FLAPJAX` (#31; `0 BNB`, `nonce = 0`, `code = 0x`)
   2. `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` — `325,000.000000000000000000 FLAPJAX` (#27, #28; `0 BNB`, `nonce = 0`, `code = 0x`)
   3. `0x405f0dbd296b580dd2798bd3597da61407bbda36` — `25,000.000000000000000000 FLAPJAX` (#12; `0 BNB`, `nonce = 0`, `code = 0x`)
   4. `0x6194e3ee19af3d68d08061f91d37e0fa00c49642` — `275,000.000000000000000000 FLAPJAX` (#1, #13; `0 BNB`, `nonce = 0`, `code = 0x`)
   5. `0x71286ec8ecb2c08ba5fc1120b27e97b517bdb058` — `300,000.000000000000000000 FLAPJAX` (#4; `0 BNB`, `nonce = 0`, `code = 0x`)
   6. `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` — `325,000.000000000000000000 FLAPJAX` (#5, #17; `0 BNB`, `nonce = 0`, `code = 0x`)
   7. `0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62` — `25,000.000000000000000000 FLAPJAX` (#14; `0 BNB`, `nonce = 0`, `code = 0x`)
   8. `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` — `25,000.000000000000000000 FLAPJAX` (#22; `0 BNB`, `nonce = 0`, `code = 0x`) — our bound holder wallet (`4,060,000 FLAPJAX` held, `100%` retention)
   9. `0xe8797a6bb4693674d78e933e85cb159a0219d03b` — `300,000.000000000000000000 FLAPJAX` (#29; `0 BNB`, `nonce = 0`, `code = 0x`)
   10. `0xeb1a0045d2477f4ae99c07e55d944ad361cfc828` — `250,000.000000000000000000 FLAPJAX` (#2; `0 BNB`, `nonce = 0`, `code = 0x`)
   11. `0xf21abef982bb1ac0308fc60887881ba640323053` — `1,125,000.000000000000000000 FLAPJAX` (#3, #19, #20; `0 BNB`, `nonce = 0`, `code = 0x`)
   12. `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` — `445,000.000000000000000000 FLAPJAX` (#21, #23, #30; `0 BNB`, `nonce = 0`, `code = 0x`)

- **Implied Operator Count (`10-27 COT`):** Across `20` distinct recipients, the `8` funded recipients collapse into **`6` distinct first-BNB funder groups** (`Group A` merges `3` Treasury-seeded recipients into 1 cluster; `Groups B–F` have 1 recipient each), while the `12` unfunded (`0 BNB`, `nonce 0`) recipients cannot be merged or separated from BNB funding alone — yielding **`18` funding buckets** (`6` funded clusters + `12` unfunded singletons). As always, first-BNB funding establishes funding links rather than proving operator identity.

---
