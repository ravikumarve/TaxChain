"""
DeFi Transaction Categorizer

Classifies DeFi interactions from raw transaction data.
Detects protocols: Uniswap V2/V3, Curve, AAVE, Compound, Morpho, Lido, etc.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DeFiCategorizer:
    """Identifies DeFi protocol interactions from transaction data."""

    PROTOCOLS = {
        "eth": {
            "uniswap_v2_router": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
            "uniswap_v3_router": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "aave_v2_lending_pool": "0x7d2768de32b0b80b7a3454c06bdac94a69ddc7a9",
            "aave_v3_pool": "0x87870bca3f3fd6335c3f4ce8392c69387b8e37e4",
            "compound_v3": "0xc3d688b66703497daa19211eedff47f25384cdc3",
            "curve_2pool": "0xbebc44782c7db0a1a60cb6fe97d0b483032ff1c7",
            "lido_steth": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
            "morpho": "0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb",
        },
        "bnb": {
            "pancakeswap_v2": "0x10ed43c718714eb63d5aa57b78b54704e256024e",
            "pancakeswap_v3": "0x13f4ea83d0bd40e75c8222255bc855a974568dd4",
            "venus": "0xfD36E2c2a6789Db23113685031d7F163291bD84c",
        },
        "polygon": {
            "quickswap": "0xa5e0829caced8ffdd4de3c43696c57f7d7a678ff",
            "aave_v3_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        },
        "arbitrum": {
            "uniswap_v3_router": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "camelot": "0xc873fecbd354f5a56e00e710b90ef4201db2448d",
            "aave_v3_pool": "0x794a61358d6845594f94dc1db02a252b5b4814ad",
        },
        "optimism": {
            "uniswap_v3_router": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "velodrome": "0x9c12939390052919af3155f41bf4160fd3666a6f",
        },
        "base": {
            "uniswap_v3_router": "0xe592427a0aece92de3edee1f18e0157c05861564",
            "aerodrome": "0xcf77a3ba9a5ca399b7c97c74d54e5b1beb874e43",
        },
    }

    METHOD_SIGNATURES = {
        "swap_exact_tokens": "0x38ed1739",
        "exact_input_single": "0x414bf389",
        "aave_deposit": "0xe8eda9df",
        "aave_borrow": "0xc5e247ef",
        "aave_repay": "0x573ade81",
        "curve_exchange": "0x3df02124",
        "add_liquidity": "0xe8e33700",
        "remove_liquidity": "0xbaa2abde",
    }

    @staticmethod
    def classify(raw_tx: Dict[str, Any], chain: str) -> Optional[str]:
        """
        Classify a raw transaction as a DeFi action.
        Returns tx_type string or None if not a DeFi action.
        """
        input_data = raw_tx.get("input", "")
        to_address = (raw_tx.get("to") or "").lower()
        method_sig = input_data[:10].lower() if len(input_data) >= 10 else ""

        if not method_sig and not to_address:
            return None

        # Check method signatures
        sig_map = {v: k for k, v in DeFiCategorizer.METHOD_SIGNATURES.items()}
        action = sig_map.get(method_sig)

        if action == "add_liquidity":
            return "lp_deposit"
        if action == "remove_liquidity":
            return "lp_withdraw"
        if action in ("aave_deposit",):
            return "yield_farm"
        if action == "aave_borrow":
            return "borrow"
        if action == "aave_repay":
            return "repay"

        # Check protocol addresses
        protocols = DeFiCategorizer.PROTOCOLS.get(chain, {})
        for name, addr in protocols.items():
            if to_address == addr:
                if "liquidity" in name or "pool" in name:
                    if "remove" in name.lower():
                        return "lp_withdraw"
                    return "lp_deposit"
                if "borrow" in name or "lending" in name:
                    return "borrow"
                if "steth" in name:
                    return "yield_farm"

        return None

    @staticmethod
    def _parse_method_signature(input_data: str) -> Optional[str]:
        if len(input_data) < 10:
            return None
        sig = input_data[:10].lower()
        sig_map = {v: k for k, v in DeFiCategorizer.METHOD_SIGNATURES.items()}
        return sig_map.get(sig)

    @staticmethod
    def _identify_protocol(to_address: str, chain: str) -> Optional[str]:
        address = to_address.lower()
        protocols = DeFiCategorizer.PROTOCOLS.get(chain, {})
        for name, addr in protocols.items():
            if address == addr:
                return name
        return None
