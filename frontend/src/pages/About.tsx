import HandsomeDan from '../components/HandsomeDan'

export default function About() {
  return (
    <section className="section about">
      <h1>About Us</h1>
      <div className="about__intro">
        <HandsomeDan size={200} chews />
        <div>
          <p className="lead">
            Campus Customs was built by a first-year MBA student at Yale who wanted a simple, low-cost
            way for students to get Yale merch.
          </p>
          <p>
            Prices seem to climb everywhere you look, from textbooks to coffee to the sweatshirt with
            your college's name on it. Showing school spirit shouldn't be another expense you have to
            plan around. The goal of this site is simple: help you gear up in Yale blue without
            breaking the bank.
          </p>
        </div>
      </div>
      <div className="perks">
        <div><h3>Simple</h3><p>Browse, filter by style or fit, and see exactly what's in stock in your size.</p></div>
        <div><h3>Low cost</h3><p>Fair prices on gear for every residential college, team and school.</p></div>
        <div><h3>Honest</h3><p>Prices and stock come straight from our inventory. No surprises at checkout.</p></div>
      </div>
    </section>
  )
}
