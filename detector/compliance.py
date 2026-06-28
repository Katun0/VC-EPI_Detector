# EPIs obrigatórios (nomes canônicos). Edite conforme a norma desejada.
REQUIRED_EPIS = ["helmet", "vest"]

# Mapeia possíveis nomes vindos do modelo para os nomes canônicos acima.
# Cobre variações comuns de datasets de EPI (PPE).
EPI_ALIASES = {
    "helmet": "helmet",
    "hardhat": "helmet",
    "hard-hat": "helmet",
    "hard_hat": "helmet",
    "capacete": "helmet",

    "vest": "vest",
    "safety-vest": "vest",
    "safety vest": "vest",
    "colete": "vest",

    "goggles": "goggles",
    "glasses": "goggles",
    "oculos": "goggles",

    "mask": "mask",
    "gloves": "gloves",
    "boots": "boots",
}


class ComplianceChecker:

    def __init__(self, required=None):
        self.required = required if required is not None else list(REQUIRED_EPIS)

    @staticmethod
    def _canonical(label):
        return EPI_ALIASES.get(label.lower(), label.lower())

    @staticmethod
    def _center(bbox):
        x1, y1, x2, y2 = bbox
        return (x1 + x2) / 2, (y1 + y2) / 2

    @staticmethod
    def _contains(person_box, point):
        x1, y1, x2, y2 = person_box
        px, py = point
        return x1 <= px <= x2 and y1 <= py <= y2

    def check(self, detections):
        """
        Recebe a lista de detecções (dicts com 'class' e 'bbox') e retorna
        um relatório de conformidade.

        Retorno:
        {
          "people": int,
          "compliant": int,
          "non_compliant": int,
          "persons": [
            {"bbox": [...], "present": [...], "missing": [...],
             "status": "Conforme"|"Nao Conforme"}
          ]
        }
        """
        persons = [d for d in detections if self._canonical(d["class"]) == "person"]
        epis = [d for d in detections if self._canonical(d["class"]) != "person"]

        report = {
            "people": len(persons),
            "compliant": 0,
            "non_compliant": 0,
            "persons": [],
        }

        for person in persons:
            present = set()

            for epi in epis:
                canonical = self._canonical(epi["class"])
                if canonical not in self.required:
                    continue
                if self._contains(person["bbox"], self._center(epi["bbox"])):
                    present.add(canonical)

            missing = [e for e in self.required if e not in present]
            status = "Conforme" if not missing else "Nao Conforme"

            if missing:
                report["non_compliant"] += 1
            else:
                report["compliant"] += 1

            report["persons"].append({
                "bbox": person["bbox"],
                "present": sorted(present),
                "missing": missing,
                "status": status,
            })

        return report
