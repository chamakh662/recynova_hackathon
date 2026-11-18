const MATERIAL_ICONS = {
  Plastique: "🧴",
  Carton: "📦",
  Papier: "📄",
  Verre: "🫙",
  Métal: "🥫",
  "Déchets divers": "♻️",
};

function DetectedMaterials({ materials = [] }) {
  return (
    <section className="detected-materials">
      <h2>Matériaux détectés par l'IA</h2>

      {materials.length === 0 ? (
        <p className="empty-state">Aucun matériau détecté.</p>
      ) : (
        <div className="detected-materials-grid">
          {materials.map((item, index) => {
            const material = item.material || item;
            const nom = material.nom || material.name || "Matériau";
            const icon = MATERIAL_ICONS[nom] || "♻️";
            const qty = item.quantite || 1;

            return (
              <div key={item.id || index} className="detected-material-pill">
                <span className="material-pill-icon">{icon}</span>
                <span className="material-pill-name">{nom}</span>
                <span className="material-pill-qty">Quantité : {qty}</span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default DetectedMaterials;
