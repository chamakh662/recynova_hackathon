import { useState } from "react";
import ImageUploader from "./ImageUploader";

const SUGGESTED_MATERIALS = [
  { nom: "Carton", icon: "📦" },
  { nom: "Plastique", icon: "🧴" },
  { nom: "Verre", icon: "🫙" },
  { nom: "Métal", icon: "🥫" },
  { nom: "Papier", icon: "📰" },
  { nom: "Bois", icon: "🪵" },
  { nom: "Tissu", icon: "🧵" },
];

function ScanForm({ onSubmit, loading }) {
  const [images, setImages] = useState([]);
  const [manualMaterials, setManualMaterials] = useState([]);
  const [customInput, setCustomInput] = useState("");
  const [budget, setBudget] = useState("10");
  const [temps, setTemps] = useState("45");
  const [difficulte, setDifficulte] = useState("facile");

  // Ajouter un matériau rapide ou personnalisé
  const handleAddMaterial = (name) => {
    const cleanName = name.trim();
    if (!cleanName) return;

    setManualMaterials((prev) => {
      const existing = prev.find(
        (m) => m.nom.toLowerCase() === cleanName.toLowerCase()
      );
      if (existing) {
        return prev.map((m) =>
          m.nom.toLowerCase() === cleanName.toLowerCase()
            ? { ...m, quantite: m.quantite + 1 }
            : m
        );
      }
      return [...prev, { nom: cleanName, quantite: 1 }];
    });
  };

  const handleUpdateQuantity = (index, delta) => {
    setManualMaterials((prev) =>
      prev
        .map((m, idx) =>
          idx === index ? { ...m, quantite: Math.max(1, m.quantite + delta) } : m
        )
        .filter((m) => m.quantite > 0)
    );
  };

  const handleRemoveMaterial = (index) => {
    setManualMaterials((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleAddCustom = (e) => {
    e.preventDefault();
    if (customInput.trim()) {
      handleAddMaterial(customInput);
      setCustomInput("");
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    if (images.length === 0 && manualMaterials.length === 0) {
      alert("Veuillez sélectionner au moins une image ou ajouter un matériau manuellement.");
      return;
    }

    const formData = new FormData();

    // 1. Ensemble des images
    images.forEach((file) => {
      formData.append("images", file);
    });
    // Rétrocompatibilité image unique
    if (images[0]) {
      formData.append("image", images[0]);
    }

    // 2. Matériaux manuels au format JSON
    if (manualMaterials.length > 0) {
      formData.append("materiaux", JSON.stringify(manualMaterials));
    }

    // 3. Paramètres du projet
    formData.append("budget", budget || "0");
    formData.append("temps_dispo", temps || "30");
    formData.append("difficulte", difficulte);

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="scan-form">
      {/* SECTION 1 : ENSEMBLE DES IMAGES */}
      <div className="scan-section">
        <h3>1. Photos des déchets</h3>
        <ImageUploader images={images} setImages={setImages} />
      </div>

      {/* SECTION 2 : MATÉRIAUX MANUELS */}
      <div className="scan-section manual-materials-section">
        <h3>2. Indiquer vos matériaux manuellement (optionnel ou complémentaire)</h3>
        <p className="section-hint">
          Sélectionnez un ou plusieurs matériaux disponibles ou saisissez le nom de votre déchet :
        </p>

        {/* Boutons de sélection rapide */}
        <div className="quick-materials-pills">
          {SUGGESTED_MATERIALS.map((mat) => (
            <button
              type="button"
              key={mat.nom}
              className="quick-pill-btn"
              onClick={() => handleAddMaterial(mat.nom)}
            >
              <span>{mat.icon}</span> {mat.nom} +
            </button>
          ))}
        </div>

        {/* Champ de saisie libre */}
        <div className="custom-material-input-row">
          <input
            type="text"
            placeholder="Autre déchet (ex: boîte de conserve, liège, pneu...)"
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
          />
          <button
            type="button"
            className="btn btn-secondary add-custom-btn"
            onClick={handleAddCustom}
          >
            + Ajouter
          </button>
        </div>

        {/* Liste des matériaux manuels sélectionnés */}
        {manualMaterials.length > 0 && (
          <div className="selected-manual-list">
            <h4>Matériaux inclus dans votre recherche :</h4>
            <div className="manual-tags-container">
              {manualMaterials.map((mat, idx) => (
                <div className="manual-material-tag" key={idx}>
                  <span className="material-tag-title">{mat.nom}</span>
                  <div className="quantity-controls">
                    <button
                      type="button"
                      onClick={() => handleUpdateQuantity(idx, -1)}
                    >
                      -
                    </button>
                    <span className="qty-val">{mat.quantite}</span>
                    <button
                      type="button"
                      onClick={() => handleUpdateQuantity(idx, 1)}
                    >
                      +
                    </button>
                  </div>
                  <button
                    type="button"
                    className="tag-remove-btn"
                    onClick={() => handleRemoveMaterial(idx)}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* SECTION 3 : PARAMÈTRES */}
      <div className="scan-section">
        <h3>3. Vos préférences de réalisation</h3>

        <div className="form-group">
          <label htmlFor="scan-budget">Votre budget maximal (DT)</label>
          <input
            id="scan-budget"
            type="number"
            min="0"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="scan-temps">Temps disponible (minutes)</label>
          <input
            id="scan-temps"
            type="number"
            min="1"
            value={temps}
            onChange={(e) => setTemps(e.target.value)}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="scan-difficulte">Niveau de difficulté souhaité</label>
          <select
            id="scan-difficulte"
            value={difficulte}
            onChange={(e) => setDifficulte(e.target.value)}
          >
            <option value="facile">Facile</option>
            <option value="moyen">Moyen</option>
            <option value="difficile">Difficile</option>
          </select>
        </div>
      </div>

      <button type="submit" className="btn btn-primary submit-scan-btn" disabled={loading}>
        {loading
          ? "Analyse IA et recherche de projets en cours..."
          : "🔍 Analyser et trouver des projets"}
      </button>
    </form>
  );
}

export default ScanForm;
