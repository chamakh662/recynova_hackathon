function ImageUploader({ images = [], setImages }) {
  const handleChange = (event) => {
    const files = Array.from(event.target.files || []);
    if (files.length > 0) {
      setImages((prev) => [...prev, ...files]);
    }
    event.target.value = "";
  };

  const handleRemove = (indexToRemove) => {
    setImages((prev) => prev.filter((_, idx) => idx !== indexToRemove));
  };

  return (
    <div className="image-uploader">
      <label htmlFor="scan-image">
        📸 Choisir ou déposer vos photos de déchets (une ou plusieurs)
      </label>
      <p className="uploader-hint">
        Sélectionnez une ou plusieurs photos (ex: carton, bouteille, bocal, canette...)
      </p>

      <input
        id="scan-image"
        type="file"
        accept="image/*"
        multiple
        onChange={handleChange}
      />

      {images.length > 0 && (
        <div className="images-preview-section">
          <div className="images-counter-badge">
            ✓ {images.length} photo{images.length > 1 ? "s" : ""} sélectionnée{images.length > 1 ? "s" : ""}
          </div>

          <div className="images-grid-preview">
            {images.map((img, index) => (
              <div className="preview-thumbnail-card" key={index}>
                <img
                  src={URL.createObjectURL(img)}
                  alt={`Aperçu ${img.name}`}
                  className="thumbnail-img"
                />
                <div className="thumbnail-footer">
                  <span className="thumbnail-name" title={img.name}>
                    {img.name}
                  </span>
                  <button
                    type="button"
                    className="thumbnail-remove-btn"
                    onClick={() => handleRemove(index)}
                    title="Supprimer cette photo"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
