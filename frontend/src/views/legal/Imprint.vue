<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Impressum</h1>
        <p class="text-lg text-gray-600">Angaben gemäß § 5 TMG</p>
      </div>

      <!-- Content -->
      <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-6 py-8">
          <!-- Anbieter -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Anbieter</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                <strong>{{ brandingData.company_name || 'ChiliView GmbH' }}</strong><br>
                {{ brandingData.address || 'Musterstraße 123' }}<br>
                {{ brandingData.postal_code || '12345' }} {{ brandingData.city || 'Musterstadt' }}<br>
                {{ brandingData.country || 'Deutschland' }}
              </p>
            </div>
          </section>

          <!-- Kontakt -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Kontakt</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                <strong>Telefon:</strong> {{ brandingData.phone || '+49 (0) 123 456789' }}<br>
                <strong>E-Mail:</strong> 
                <a :href="`mailto:${brandingData.email || 'info@chiliview.com'}`" 
                   class="text-blue-600 hover:text-blue-800">
                  {{ brandingData.email || 'info@chiliview.com' }}
                </a><br>
                <strong>Website:</strong> 
                <a :href="brandingData.website || 'https://chiliview.com'" 
                   class="text-blue-600 hover:text-blue-800" 
                   target="_blank" 
                   rel="noopener noreferrer">
                  {{ brandingData.website || 'https://chiliview.com' }}
                </a>
              </p>
            </div>
          </section>

          <!-- Geschäftsführung -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Geschäftsführung</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                {{ brandingData.ceo || 'Max Mustermann' }}
              </p>
            </div>
          </section>

          <!-- Registereintrag -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Registereintrag</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                <strong>Registergericht:</strong> {{ brandingData.register_court || 'Amtsgericht Musterstadt' }}<br>
                <strong>Registernummer:</strong> {{ brandingData.register_number || 'HRB 12345' }}
              </p>
            </div>
          </section>

          <!-- Umsatzsteuer-ID -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Umsatzsteuer-Identifikationsnummer</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Gemäß § 27 a Umsatzsteuergesetz:<br>
                <strong>{{ brandingData.vat_id || 'DE123456789' }}</strong>
              </p>
            </div>
          </section>

          <!-- Verantwortlich für den Inhalt -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                {{ brandingData.content_responsible || 'Max Mustermann' }}<br>
                {{ brandingData.address || 'Musterstraße 123' }}<br>
                {{ brandingData.postal_code || '12345' }} {{ brandingData.city || 'Musterstadt' }}
              </p>
            </div>
          </section>

          <!-- Haftungsausschluss -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Haftungsausschluss</h2>
            
            <h3 class="text-lg font-medium text-gray-900 mb-3">Haftung für Inhalte</h3>
            <div class="prose prose-gray max-w-none mb-6">
              <p class="text-gray-700 leading-relaxed">
                Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den 
                allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht 
                unter der Verpflichtung, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach 
                Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.
              </p>
              <p class="text-gray-700 leading-relaxed">
                Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen 
                Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt 
                der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden 
                Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.
              </p>
            </div>

            <h3 class="text-lg font-medium text-gray-900 mb-3">Haftung für Links</h3>
            <div class="prose prose-gray max-w-none mb-6">
              <p class="text-gray-700 leading-relaxed">
                Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. 
                Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der 
                verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich.
              </p>
            </div>

            <h3 class="text-lg font-medium text-gray-900 mb-3">Urheberrecht</h3>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem 
                deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung 
                außerhalb der Grenzen des Urheberrechtes bedürfen der schriftlichen Zustimmung des jeweiligen 
                Autors bzw. Erstellers.
              </p>
            </div>
          </section>

          <!-- EU-Streitschlichtung -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">EU-Streitschlichtung</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: 
                <a href="https://ec.europa.eu/consumers/odr/" 
                   class="text-blue-600 hover:text-blue-800" 
                   target="_blank" 
                   rel="noopener noreferrer">
                  https://ec.europa.eu/consumers/odr/
                </a>
              </p>
              <p class="text-gray-700 leading-relaxed">
                Unsere E-Mail-Adresse finden Sie oben im Impressum.
              </p>
            </div>
          </section>

          <!-- Verbraucherstreitbeilegung -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer 
                Verbraucherschlichtungsstelle teilzunehmen.
              </p>
            </div>
          </section>
        </div>
      </div>

      <!-- Footer Navigation -->
      <div class="mt-12 text-center">
        <div class="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
          <router-link to="/privacy" class="hover:text-gray-900">Datenschutzerklärung</router-link>
          <router-link to="/terms" class="hover:text-gray-900">AGB</router-link>
          <router-link to="/" class="hover:text-gray-900">Zurück zur Startseite</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useBrandingService } from '@/services/branding'

export default {
  name: 'Imprint',
  setup() {
    const brandingData = ref({})
    const { loadBranding } = useBrandingService()

    onMounted(async () => {
      // 🎨 Branding-Daten laden falls verfügbar
      try {
        const branding = await loadBranding()
        brandingData.value = branding || {}
      } catch (error) {
        console.warn('Branding-Daten konnten nicht geladen werden:', error)
        brandingData.value = {}
      }
    })

    return {
      brandingData
    }
  }
}
</script>

<style scoped>
.prose {
  max-width: none;
}

.prose p {
  margin-bottom: 1rem;
}

.prose a {
  text-decoration: underline;
}

.prose a:hover {
  text-decoration: none;
}
</style>