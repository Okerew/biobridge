from biobridge.blocks.protein import Protein
from typing import Optional, List, Dict

class Enzyme(Protein):
    def __init__(self, name: str, sequence: str, substrate: str, 
                 product: str, km: float = 1.0, vmax: float = 10.0, 
                 ph_optimum: float = 7.0, temperature_optimum: float = 37.0,
                 cofactors: Optional[List[str]] = None, 
                 inhibitors: Optional[List[str]] = None):
        super().__init__(name, sequence)
        self.substrate = substrate
        self.product = product
        self.km = km
        self.vmax = vmax
        self.ph_optimum = ph_optimum
        self.temperature_optimum = temperature_optimum
        self.cofactors = cofactors or []
        self.inhibitors = inhibitors or []
        self.activity = 1.0
        self.is_allosteric = False
        self.allosteric_sites = []

    def catalyze(self, substrate_concentration: float, 
                ph: float = 7.0, temperature: float = 37.0,
                inhibitor_concentrations: Optional[Dict[str, float]] = None,
                cofactor_concentrations: Optional[Dict[str, float]] = None) -> float:
        inhibitor_concentrations = inhibitor_concentrations or {}
        cofactor_concentrations = cofactor_concentrations or {}
        
        activity_factor = self.activity
        
        ph_factor = 1.0 - abs(ph - self.ph_optimum) * 0.2
        ph_factor = max(0.1, ph_factor)
        
        temp_factor = 1.0 - abs(temperature - self.temperature_optimum) * 0.05
        temp_factor = max(0.1, temp_factor)
        
        cofactor_factor = 1.0
        for cofactor in self.cofactors:
            if cofactor not in cofactor_concentrations:
                cofactor_factor *= 0.3
            else:
                cofactor_factor *= min(1.0, cofactor_concentrations[cofactor])
        
        inhibitor_factor = 1.0
        for inhibitor in self.inhibitors:
            if inhibitor in inhibitor_concentrations:
                inhibitor_factor *= (1.0 / (1.0 + 
                                           inhibitor_concentrations[inhibitor]))
        
        michaelis_menten = (self.vmax * substrate_concentration) / (
            self.km + substrate_concentration)
        
        reaction_rate = (michaelis_menten * activity_factor * ph_factor * 
                        temp_factor * cofactor_factor * inhibitor_factor)
        
        return max(0, reaction_rate)

    def add_allosteric_site(self, effector: str, effect_type: str = "positive"):
        self.is_allosteric = True
        self.allosteric_sites.append({"effector": effector, 
                                     "type": effect_type})

    def allosteric_regulation(self, effector_concentrations: Dict[str, float]) -> float:
        if not self.is_allosteric:
            return 1.0
        
        regulation_factor = 1.0
        for site in self.allosteric_sites:
            effector = site["effector"]
            if effector in effector_concentrations:
                concentration = effector_concentrations[effector]
                if site["type"] == "positive":
                    regulation_factor *= (1.0 + concentration * 0.5)
                else:
                    regulation_factor *= (1.0 / (1.0 + concentration))
        
        return regulation_factor

class EnzymePathway:
    def __init__(self, name: str, enzymes: List[Enzyme]):
        self.name = name
        self.enzymes = enzymes
        self.metabolites = {}
        self.flux_rate = 1.0
        self.regulation_status = "active"

    def run_pathway(self, initial_substrate: str, 
                   substrate_amount: float,
                   conditions: Dict[str, float] = None) -> Dict[str, float]:
        conditions = conditions or {"ph": 7.0, "temperature": 37.0}
        
        current_substrate = initial_substrate
        current_amount = substrate_amount
        products = {}
        
        for enzyme in self.enzymes:
            if enzyme.substrate == current_substrate or current_substrate == "any":
                reaction_rate = enzyme.catalyze(current_amount, **conditions)
                product_amount = min(current_amount, reaction_rate)
                
                products[enzyme.product] = products.get(enzyme.product, 0) + product_amount
                current_substrate = enzyme.product
                current_amount = product_amount
        
        return products

    def add_feedback_inhibition(self, end_product: str, 
                              target_enzyme: Enzyme) -> None:
        if end_product not in target_enzyme.inhibitors:
            target_enzyme.inhibitors.append(end_product)

    def regulate_pathway(self, regulation_type: str, factor: float = 1.0):
        if regulation_type == "upregulate":
            for enzyme in self.enzymes:
                enzyme.activity *= factor
            self.regulation_status = "upregulated"
        elif regulation_type == "downregulate":
            for enzyme in self.enzymes:
                enzyme.activity /= factor
            self.regulation_status = "downregulated"

