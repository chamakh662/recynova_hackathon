import RegisterForm from "../components/RegisterForm";

function Register() {
  return (
    <section className="auth-page">
      <div className="auth-card">
        <h1>Créer un compte</h1>
        <p>Rejoignez RecyNova et transformez vos déchets en ressources.</p>
        <RegisterForm />
      </div>
    </section>
  );
}

export default Register;