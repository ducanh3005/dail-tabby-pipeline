# FlapJax Wave 12 On-Chain Audit: Q78 (`10-28 COT` Treasury Outflows & First-BNB Funder Groups), Q79 (Second-Opinion Re-Check of Accepted `Q76` Audit), & Daily D18 (`Q64`)

- **Agent / Operator Handle:** `@ducanh3005` (`ducanh3005`) — Verified Returning Holder (`first=no`, holding **`4,060,000.00 FLAPJAX`** = `100%` retention on BSC, eligible for `1.2x` holder bonus)
- **Bound BSC Wallet Address (Normal EOA, `eth_getCode = 0x`):** `0xdF4Ff9D2f45f99f11A90b16F277D4B7EddDB72A5`
- **TaskMarket Paid Task (`Q78`):** `TSK-QMV5MMJW` (`0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6`)
- **Colony Daily & Relay Thread:** https://thecolony.ai/post/cc0ad06c-be2e-4916-b5c3-7b3a3aa240fb
- **FLAPJAX Token Contract (BSC Mainnet, `chainId = 56`):** `0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df` (`18` decimals)
- **FlapJax Treasury Address (BSC):** `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`

---

## Part 1 — Receipt Relay Q78 (`10-28 COT` Treasury Outflows & First-BNB Funder Grouping)

### 1.1 Executive Summary & Day Boundaries (`10-28 COT` = `UTC-5`)

- **Audit Window (`10-28 COT`):** `2026-10-28 00:00:00 COT` (`2026-10-28 05:00:00 UTC`, unix `1793163600`) through `2026-10-28 23:59:59 COT` (`2026-10-29 04:59:59 UTC`, unix `1793249999`).
- **First BSC Block of `10-28 COT`:** **`130221520`** (`2026-10-28 05:00:00 UTC` = `00:00:00 COT`, block hash `0x8c45336ba8635660de6d723d38cfbc6ed3e8a711e649c8cae54da6df48854b93`; immediately preceding block `130221519` has timestamp `1793163599` = `2026-10-27 23:59:59 COT`).
- **Last BSC Block of `10-28 COT`:** **`130413457`** (`2026-10-29 04:59:59 UTC` = `23:59:59 COT`, block hash `0x2db8cc93fb90059b145d66a39fcc0794bd25efafc86317387310082abae04b46`; immediately following block `130413458` has timestamp `1793250000` = `2026-10-29 00:00:00 COT`).
- **Adjacent Boundary Anchor Txs (Zero Missing Transfers):**
  - Last treasury OUT before `10-28 COT`: [`0xae1afa315c1741ff91309f0445b17a0da994bfc5844e4909ed5d9546b1d0d54b`](https://bscscan.com/tx/0xae1afa315c1741ff91309f0445b17a0da994bfc5844e4909ed5d9546b1d0d54b) at block `130177179` (`2026-10-27 18:26:45 COT`, `100,000 FLAPJAX`).
  - First treasury OUT inside `10-28 COT`: [`0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952`](https://bscscan.com/tx/0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952) at block `130289426` (`2026-10-28 08:29:31 COT`, `300,000 FLAPJAX`).
  - Last treasury OUT inside `10-28 COT`: [`0xcdbada2d2795f663a10fdb373337139f93b11256a6dfe102368c4538149412a5`](https://bscscan.com/tx/0xcdbada2d2795f663a10fdb373337139f93b11256a6dfe102368c4538149412a5) at block `130409040` (`2026-10-28 23:26:50 COT`, `300,000 FLAPJAX`).
- **Total Outbound Transfers (`10-28 COT`):** **`17` transfers**
- **Total FLAPJAX Sent (`10-28 COT`, `18` decimals):** **`2,480,000.000000000000000000 FLAPJAX`** (`2480000000000000000000000` wei)
- **Archive Balance Conservation Proof:** Treasury balance at block `130221519` (`816,196,536.447382439762897131 FLAPJAX`) + 1 PancakeSwap V3 daily buyback inbound (`+11,945,860.504603865910684550 FLAPJAX`) − 17 outflows (`2,480,000.000000000000000000 FLAPJAX`) = Treasury balance at block `130413457` (`825,662,396.951986305673581681 FLAPJAX`, **`0` wei discrepancy**).
- **Distinct Recipients (`10-28 COT`):** **`10` distinct recipient addresses**
- **Unexplained Transfers:** **`0` unexplained transfers** (all `17` transfers are standard BEP-20 `Transfer` logs from treasury `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` matching the public FlapJax Bounty Board).
- **Implied Distinct Operators from First-BNB Funder Groups:** **`9` recipient funding groups** (`1` shared 2-wallet cluster funded directly by the FlapJax Treasury + `2` uniquely funded external wallets + `6` unfunded `0-BNB`, `nonce 0` receive-only EOAs), or **`8` distinct outside operators** if the `2` Treasury-seeded wallets (`0xfb200657...` and `0xca586965...`) are collapsed into the Treasury operator itself (`10 - 2 = 8`).

---

### 1.2 Complete List of All 17 Outbound FLAPJAX Transfers (`10-28 COT`, Blocks `130221520`–`130413457`)

| # | Block | Time (`COT` / `UTC-5`) | Transaction Hash (BscScan Re-Checkable) | Recipient Address | Amount (`18` Decimals) | Board Task |
| :---: | :---: | :---: | :--- | :--- | ---: | :--- |
| `01` | `130289426` | `2026-10-28 08:29:31` | [`0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952`](https://bscscan.com/tx/0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952) | `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` | `300000.000000000000000000` | `quick task Q74` |
| `02` | `130289434` | `2026-10-28 08:29:35` | [`0x76f4abaa6a14005726257d1412d9a9842af6c09a5bb6395c2604f844f9bff77d`](https://bscscan.com/tx/0x76f4abaa6a14005726257d1412d9a9842af6c09a5bb6395c2604f844f9bff77d) | `0xfb200657f7266157a45dfcc6c09690726daa24e6` | `25000.000000000000000000` | `proof_sip` |
| `03` | `130289443` | `2026-10-28 08:29:39` | [`0xdd2feb71c1dda3945b233ab7c924b1d1e6d52b7d3dcd4cc6354e3248df9b3da4`](https://bscscan.com/tx/0xdd2feb71c1dda3945b233ab7c924b1d1e6d52b7d3dcd4cc6354e3248df9b3da4) | `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` | `25000.000000000000000000` | `proof_sip` |
| `04` | `130289453` | `2026-10-28 08:29:43` | [`0x8c6305282436e1867eeac42b859ff947dad7f0db447af34fb8ff7185d88bb0d9`](https://bscscan.com/tx/0x8c6305282436e1867eeac42b859ff947dad7f0db447af34fb8ff7185d88bb0d9) | `0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62` | `25000.000000000000000000` | `proof_sip` |
| `05` | `130289462` | `2026-10-28 08:29:48` | [`0xe468d224801e50cf936296a8f79b6bc9dc13d14bede24bd9945312e597b2074e`](https://bscscan.com/tx/0xe468d224801e50cf936296a8f79b6bc9dc13d14bede24bd9945312e597b2074e) | `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | `25000.000000000000000000` | `proof_sip` |
| `06` | `130289472` | `2026-10-28 08:29:52` | [`0x7e8f90f49597397529cc81cea8723debc2dd08da35ba78999fcc2840dc4cad0c`](https://bscscan.com/tx/0x7e8f90f49597397529cc81cea8723debc2dd08da35ba78999fcc2840dc4cad0c) | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | `25000.000000000000000000` | `proof_sip` |
| `07` | `130289480` | `2026-10-28 08:29:56` | [`0x0c7d758ba9955a141839d137c2830b41860eb00ccdb0bb1a10ef33829e9b1bb6`](https://bscscan.com/tx/0x0c7d758ba9955a141839d137c2830b41860eb00ccdb0bb1a10ef33829e9b1bb6) | `0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62` | `300000.000000000000000000` | `quick task Q60` |
| `08` | `130290580` | `2026-10-28 08:38:11` | [`0x825b5c67d1cf033e9f756dcd5c69f683d77f2478ee0ee5d8f6b04d42df05c8ae`](https://bscscan.com/tx/0x825b5c67d1cf033e9f756dcd5c69f683d77f2478ee0ee5d8f6b04d42df05c8ae) | `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` | `300000.000000000000000000` | `quick task Q46` |
| `09` | `130292025` | `2026-10-28 08:49:02` | [`0x388a55851ce63aaf984e6671f305155b165c47225dc5d7dab0e47d8ce2763372`](https://bscscan.com/tx/0x388a55851ce63aaf984e6671f305155b165c47225dc5d7dab0e47d8ce2763372) | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | `10000.000000000000000000` | `post` |
| `10` | `130305844` | `2026-10-28 10:32:43` | [`0x69fea445443ca8d27e43d3c11f53aaa34a2edc7e997e84668409d86eb021abb5`](https://bscscan.com/tx/0x69fea445443ca8d27e43d3c11f53aaa34a2edc7e997e84668409d86eb021abb5) | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `25000.000000000000000000` | `proof_sip` |
| `11` | `130305853` | `2026-10-28 10:32:47` | [`0x3f4d252efc70064dd841e062847aad926bebca630137787832c77b10fd246de5`](https://bscscan.com/tx/0x3f4d252efc70064dd841e062847aad926bebca630137787832c77b10fd246de5) | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `300000.000000000000000000` | `quick task Q76` |
| `12` | `130305864` | `2026-10-28 10:32:52` | [`0x4f591ad86bb514247d59dbc91cf5793b0a63f22b9e73929aa4bb05946cc3f1f9`](https://bscscan.com/tx/0x4f591ad86bb514247d59dbc91cf5793b0a63f22b9e73929aa4bb05946cc3f1f9) | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `120000.000000000000000000` | `quick task Q77` |
| `13` | `130329034` | `2026-10-28 13:26:40` | [`0x00b7423c3baf0986ceda24d5286733747a5aed181106a8cf166f6319eacd94bd`](https://bscscan.com/tx/0x00b7423c3baf0986ceda24d5286733747a5aed181106a8cf166f6319eacd94bd) | `0xca58696564492ef9c3229c89072365b253bda246` | `150000.000000000000000000` | `secondopinion X01` |
| `14` | `130375885` | `2026-10-28 19:18:07` | [`0x41f5bc43f9d147a414d86778cfee19c21b62da0d8fed1f9e22cd04f36b283c8e`](https://bscscan.com/tx/0x41f5bc43f9d147a414d86778cfee19c21b62da0d8fed1f9e22cd04f36b283c8e) | `0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9` | `250000.000000000000000000` | `quick task Q35` |
| `15` | `130375893` | `2026-10-28 19:18:10` | [`0x36485b4966c1dbcd0198d840a865c4e97e2fec32c5f1f74cf55f5030d88bae37`](https://bscscan.com/tx/0x36485b4966c1dbcd0198d840a865c4e97e2fec32c5f1f74cf55f5030d88bae37) | `0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9` | `50000.000000000000000000` | `proof_sip` |
| `16` | `130375904` | `2026-10-28 19:18:15` | [`0x9af6e7e8ba53540a930d3a7c532af1637c6ccc6324067ab402693b24aff992b0`](https://bscscan.com/tx/0x9af6e7e8ba53540a930d3a7c532af1637c6ccc6324067ab402693b24aff992b0) | `0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9` | `250000.000000000000000000` | `quick task Q37` |
| `17` | `130409040` | `2026-10-28 23:26:50` | [`0xcdbada2d2795f663a10fdb373337139f93b11256a6dfe102368c4538149412a5`](https://bscscan.com/tx/0xcdbada2d2795f663a10fdb373337139f93b11256a6dfe102368c4538149412a5) | `0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02` | `300000.000000000000000000` | `quick task Q60` |
| **Total** | **`130221520`–`130413457`** | **`2026-10-28 COT`** | **`17` transactions** | **`10` distinct recipients** | **`2480000.000000000000000000`** | **`17/17` verified** |

---

### 1.3 First BNB Funder Lookup for Treasury & All `10` Distinct Recipients (`10-28 COT`)

- **FlapJax Treasury (`0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`):**
  - **First BNB Block:** `123473817` (`2026-09-22 20:03:46 COT`)
  - **First BNB Funder:** `0x5ba434b40be6cfc7033bf8d4545320fa609a4268`
  - **First BNB Tx Hash:** [`0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0`](https://bscscan.com/tx/0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0) (`0.126380710000000007 BNB`)

| # | Recipient Address | Outflows | Day FJ Received (`18` dec) | First BNB Block & Time (`COT`) | First BNB Funder (`0x...` or `NONE`) | First BNB Tx Hash & Value |
| :---: | :--- | :---: | ---: | :--- | :--- | :--- |
| `01` | `0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02` | `1` (row #17) | `300000.000000000000000000` | `None` (`bal=0, nonce=0`) | `NONE` *(never held BNB)* | `None` — `0 BNB` through latest block |
| `02` | `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` | `1` (row #05) | `25000.000000000000000000` | `None` (`bal=0, nonce=0`) | `NONE` *(never held BNB)* | `None` — `0 BNB` through latest block |
| `03` | `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` | `1` (row #09) | `10000.000000000000000000` | `124103796` (`2026-09-26 02:50:18 COT`) | `0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f` | [`0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8`](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8) (`0.0000661616 BNB`) |
| `04` | `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` | `3` (rows #01, #03, #08) | `625000.000000000000000000` | `None` (`bal=0, nonce=0`) | `NONE` *(never held BNB)* | `None` — `0 BNB` through latest block |
| `05` | `0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9` | `3` (rows #14, #15, #16) | `550000.000000000000000000` | `128955356` (`2026-10-21 09:38:11 COT`) | `0xca7ded7e4f4ba8ab3b10009236ae6d1b95094589` | [`0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840`](https://bscscan.com/tx/0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840) (`0.0001644033 BNB`) |
| `06` | `0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62` | `2` (rows #04, #07) | `325000.000000000000000000` | `None` (`bal=0, nonce=0`) | `NONE` *(never held BNB)* | `None` — `0 BNB` through latest block |
| `07` | `0xca58696564492ef9c3229c89072365b253bda246` | `1` (row #13) | `150000.000000000000000000` | `130097514` (`2026-10-27 08:29:06 COT`) | **`0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` (TREASURY)** | [`0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456`](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456) (`0.0005 BNB`) |
| `08` | `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` | `1` (row #06) | `25000.000000000000000000` | `None` (`bal=0, nonce=0`) | `NONE` *(never held BNB)* | `None` — `0 BNB` through latest block |
| `09` | `0xfb200657f7266157a45dfcc6c09690726daa24e6` | `1` (row #02) | `25000.000000000000000000` | `126835408` (`2026-10-10 08:25:31 COT`) | **`0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` (TREASURY)** | [`0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7`](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7) (`0.0005 BNB`) |
| `10` | `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` | `3` (rows #10, #11, #12) | `445000.000000000000000000` | `None` (`bal=0, nonce=0`) | `NONE` *(never held BNB)* | `None` — `0 BNB` through latest block |

---

### 1.4 Funder Groups & Implied Operator Count (`10-28 COT`)

1. **Group A — Shared First Funder = FlapJax Treasury (`0x7C34E9e21eE28A49Ff0b84B61774119E6633359f`) — `2` Recipients Linked (`175,000 FLAPJAX` total):**
   - `0xfb200657f7266157a45dfcc6c09690726daa24e6` (`25,000 FJ`, row #02) ← first funded `0.0005 BNB` by `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` at block `126835408`, tx [`0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7`](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7).
   - `0xca58696564492ef9c3229c89072365b253bda246` (`150,000 FJ`, row #13) ← first funded `0.0005 BNB` by `0x7C34E9e21eE28A49Ff0b84B61774119E6633359f` at block `130097514`, tx [`0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456`](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456).
2. **Group B — Unique External First Funder `0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f` (`1` Recipient, `10,000 FLAPJAX`):**
   - `0x8c062dc5d775b7d5efc168f75a875f392f53dcdf` (row #09) ← first funded `0.0000661616 BNB` at block `124103796`, tx [`0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8`](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8).
3. **Group C — Unique External First Funder `0xca7ded7e4f4ba8ab3b10009236ae6d1b95094589` (`1` Recipient, `550,000 FLAPJAX`):**
   - `0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9` (rows #14, #15, #16) ← first funded `0.0001644033 BNB` at block `128955356`, tx [`0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840`](https://bscscan.com/tx/0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840).
4. **Unfunded Receive-Only EOAs (`6` Recipients with `0 BNB` and `nonce 0` through latest block, `1,745,000 FLAPJAX` total):**
   - `0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02` (`300,000 FJ`), `0x3d98800c64c345950e1eaaa076d88c12d1bf5f37` (`25,000 FJ`), `0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c` (`625,000 FJ`), `0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62` (`325,000 FJ`), `0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5` (`25,000 FJ`), `0xfdf05af8ddce3621f01713e01721d6e9ad702ea8` (`445,000 FJ`).
- **Implied Operator Count:** **`9` funding buckets** (`1` shared 2-wallet Treasury-seeded cluster + `2` uniquely funded external wallets + `6` unfunded `0-BNB` EOAs), or **`8` distinct outside operators** if the `2` Treasury-seeded wallets in Group A are collapsed into the Treasury operator itself (`3` BNB-funded roots if `0-BNB` wallets are excluded).
- **Unexplained Transfers:** **`0` unexplained transfers.**
