<template>
  <div class="min-h-screen bg-gray-50 py-12">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Datenschutzerklärung</h1>
        <p class="text-lg text-gray-600">Informationen zur Verarbeitung Ihrer personenbezogenen Daten</p>
        <p class="text-sm text-gray-500 mt-2">Stand: {{ new Date().toLocaleDateString('de-DE') }}</p>
      </div>

      <!-- Content -->
      <div class="bg-white shadow-sm rounded-lg overflow-hidden">
        <div class="px-6 py-8">
          <!-- Einleitung -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">1. Datenschutz auf einen Blick</h2>
            
            <h3 class="text-lg font-medium text-gray-900 mb-3">Allgemeine Hinweise</h3>
            <div class="prose prose-gray max-w-none mb-6">
              <p class="text-gray-700 leading-relaxed">
                Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen 
                Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit 
                denen Sie persönlich identifiziert werden können.
              </p>
            </div>

            <h3 class="text-lg font-medium text-gray-900 mb-3">Datenerfassung auf dieser Website</h3>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                <strong>Wer ist verantwortlich für die Datenerfassung auf dieser Website?</strong><br>
                Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber. Dessen Kontaktdaten 
                können Sie dem Abschnitt „Hinweis zur Verantwortlichen Stelle" in dieser Datenschutzerklärung entnehmen.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Wie erfassen wir Ihre Daten?</strong><br>
                Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen. Hierbei kann es sich 
                z.B. um Daten handeln, die Sie in ein Kontaktformular eingeben oder bei der Registrierung angeben.
              </p>
            </div>
          </section>

          <!-- Verantwortliche Stelle -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">2. Verantwortliche Stelle</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>{{ brandingData.company_name || 'ChiliView GmbH' }}</strong><br>
                {{ brandingData.address || 'Musterstraße 123' }}<br>
                {{ brandingData.postal_code || '12345' }} {{ brandingData.city || 'Musterstadt' }}<br>
                <br>
                Telefon: {{ brandingData.phone || '+49 (0) 123 456789' }}<br>
                E-Mail: 
                <a :href="`mailto:${brandingData.email || 'info@chiliview.com'}`" 
                   class="text-blue-600 hover:text-blue-800">
                  {{ brandingData.email || 'info@chiliview.com' }}
                </a>
              </p>
              <p class="text-gray-700 leading-relaxed">
                Verantwortliche Stelle ist die natürliche oder juristische Person, die allein oder gemeinsam 
                mit anderen über die Zwecke und Mittel der Verarbeitung von personenbezogenen Daten entscheidet.
              </p>
            </div>
          </section>

          <!-- Datenschutzbeauftragter -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">3. Datenschutzbeauftragter</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Wir haben einen Datenschutzbeauftragten bestellt:
              </p>
              <p class="text-gray-700 leading-relaxed">
                {{ brandingData.dpo_name || 'Max Mustermann' }}<br>
                {{ brandingData.dpo_address || brandingData.address || 'Musterstraße 123' }}<br>
                {{ brandingData.postal_code || '12345' }} {{ brandingData.city || 'Musterstadt' }}<br>
                <br>
                Telefon: {{ brandingData.dpo_phone || brandingData.phone || '+49 (0) 123 456789' }}<br>
                E-Mail: 
                <a :href="`mailto:${brandingData.dpo_email || 'datenschutz@chiliview.com'}`" 
                   class="text-blue-600 hover:text-blue-800">
                  {{ brandingData.dpo_email || 'datenschutz@chiliview.com' }}
                </a>
              </p>
            </div>
          </section>

          <!-- Datenverarbeitung -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">4. Datenverarbeitung auf dieser Website</h2>
            
            <h3 class="text-lg font-medium text-gray-900 mb-3">Cookies</h3>
            <div class="prose prose-gray max-w-none mb-6">
              <p class="text-gray-700 leading-relaxed">
                Unsere Internetseiten verwenden so genannte „Cookies". Cookies sind kleine Datenpakete und 
                richten auf Ihrem Endgerät keinen Schaden an. Sie werden entweder vorübergehend für die 
                Dauer einer Sitzung (Session-Cookies) oder dauerhaft (permanente Cookies) auf Ihrem Endgerät 
                gespeichert.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Technisch notwendige Cookies:</strong> Diese Cookies sind für die Grundfunktionen 
                der Website erforderlich und können nicht deaktiviert werden. Sie speichern keine 
                personenbezogenen Daten.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Funktionale Cookies:</strong> Diese Cookies ermöglichen erweiterte Funktionen 
                und Personalisierung. Sie können von uns oder von Drittanbietern gesetzt werden.
              </p>
            </div>

            <h3 class="text-lg font-medium text-gray-900 mb-3">Server-Log-Dateien</h3>
            <div class="prose prose-gray max-w-none mb-6">
              <p class="text-gray-700 leading-relaxed">
                Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten 
                Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt:
              </p>
              <ul class="list-disc list-inside text-gray-700 leading-relaxed ml-4">
                <li>Browsertyp und Browserversion</li>
                <li>Verwendetes Betriebssystem</li>
                <li>Referrer URL</li>
                <li>Hostname des zugreifenden Rechners</li>
                <li>Uhrzeit der Serveranfrage</li>
                <li>IP-Adresse</li>
              </ul>
              <p class="text-gray-700 leading-relaxed">
                Diese Daten werden nicht mit anderen Datenquellen zusammengeführt. Die Erfassung dieser 
                Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO.
              </p>
            </div>

            <h3 class="text-lg font-medium text-gray-900 mb-3">Registrierung auf dieser Website</h3>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Sie können sich auf dieser Website registrieren, um zusätzliche Funktionen zu nutzen. 
                Die dazu eingegebenen Daten verwenden wir nur zum Zwecke der Nutzung des jeweiligen 
                Angebotes oder Dienstes, für den Sie sich registriert haben.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Verarbeitete Daten bei der Registrierung:</strong>
              </p>
              <ul class="list-disc list-inside text-gray-700 leading-relaxed ml-4">
                <li>Benutzername</li>
                <li>E-Mail-Adresse</li>
                <li>Vollständiger Name</li>
                <li>Passwort (verschlüsselt gespeichert)</li>
                <li>Registrierungsdatum</li>
                <li>IP-Adresse zum Zeitpunkt der Registrierung</li>
              </ul>
            </div>
          </section>

          <!-- 3D-Modell Upload -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">5. 3D-Modell Upload und Verarbeitung</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                <strong>Zweck der Datenverarbeitung:</strong><br>
                Wenn Sie Bilder für die 3D-Modellierung hochladen, verarbeiten wir diese Daten ausschließlich 
                zum Zweck der Erstellung von 3D-Modellen mittels Photogrammetrie-Verfahren.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Verarbeitete Daten:</strong>
              </p>
              <ul class="list-disc list-inside text-gray-700 leading-relaxed ml-4">
                <li>Hochgeladene Bilddateien</li>
                <li>EXIF-Daten der Bilder (GPS-Koordinaten, Kameraeinstellungen)</li>
                <li>Generierte 3D-Modelle und Punktwolken</li>
                <li>Verarbeitungsprotokoll und Metadaten</li>
              </ul>
              <p class="text-gray-700 leading-relaxed">
                <strong>Speicherdauer:</strong> Ihre Projektdaten werden für die Dauer Ihres Accounts 
                gespeichert. Sie können jederzeit einzelne Projekte oder Ihren gesamten Account löschen.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Rechtsgrundlage:</strong> Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung)
              </p>
            </div>
          </section>

          <!-- Ihre Rechte -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">6. Ihre Rechte</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Sie haben gegenüber uns folgende Rechte hinsichtlich der Sie betreffenden personenbezogenen Daten:
              </p>
              <ul class="list-disc list-inside text-gray-700 leading-relaxed ml-4">
                <li><strong>Recht auf Auskunft</strong> (Art. 15 DSGVO)</li>
                <li><strong>Recht auf Berichtigung</strong> (Art. 16 DSGVO)</li>
                <li><strong>Recht auf Löschung</strong> (Art. 17 DSGVO)</li>
                <li><strong>Recht auf Einschränkung der Verarbeitung</strong> (Art. 18 DSGVO)</li>
                <li><strong>Recht auf Datenübertragbarkeit</strong> (Art. 20 DSGVO)</li>
                <li><strong>Widerspruchsrecht</strong> (Art. 21 DSGVO)</li>
                <li><strong>Recht auf Beschwerde bei einer Aufsichtsbehörde</strong> (Art. 77 DSGVO)</li>
              </ul>
              <p class="text-gray-700 leading-relaxed">
                <strong>Widerruf von Einwilligungen:</strong> Sofern die Verarbeitung der personenbezogenen 
                Daten auf einer erteilten Einwilligung beruht, haben Sie jederzeit das Recht, die Einwilligung 
                zu widerrufen. Durch den Widerruf der Einwilligung wird die Rechtmäßigkeit der aufgrund der 
                Einwilligung bis zum Widerruf erfolgten Verarbeitung nicht berührt.
              </p>
            </div>
          </section>

          <!-- Datensicherheit -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">7. Datensicherheit</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Wir verwenden innerhalb des Website-Besuchs das verbreitete SSL-Verfahren (Secure Socket Layer) 
                in Verbindung mit der jeweils höchsten Verschlüsselungsstufe, die von Ihrem Browser unterstützt wird.
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Technische und organisatorische Maßnahmen:</strong>
              </p>
              <ul class="list-disc list-inside text-gray-700 leading-relaxed ml-4">
                <li>Verschlüsselung der Datenübertragung (HTTPS/TLS)</li>
                <li>Verschlüsselte Speicherung von Passwörtern</li>
                <li>Regelmäßige Sicherheitsupdates</li>
                <li>Zugriffskontrolle und Berechtigungsmanagement</li>
                <li>Regelmäßige Datensicherungen</li>
                <li>Protokollierung von Systemzugriffen</li>
              </ul>
            </div>
          </section>

          <!-- Datenübertragung -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">8. Datenübertragung in Drittländer</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Eine Übertragung Ihrer personenbezogenen Daten in Drittländer (Länder außerhalb des 
                Europäischen Wirtschaftsraums) findet grundsätzlich nicht statt. Sollte dies in Einzelfällen 
                erforderlich sein, erfolgt dies nur bei Vorliegen einer Einwilligung oder auf Grundlage 
                angemessener Garantien im Sinne der Art. 44 ff. DSGVO.
              </p>
            </div>
          </section>

          <!-- Aufbewahrungsfristen -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">9. Aufbewahrungsfristen</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Personenbezogene Daten werden nur so lange gespeichert, wie es für den jeweiligen Zweck 
                erforderlich ist oder gesetzliche Aufbewahrungsfristen bestehen:
              </p>
              <ul class="list-disc list-inside text-gray-700 leading-relaxed ml-4">
                <li><strong>Account-Daten:</strong> Bis zur Löschung des Accounts</li>
                <li><strong>Projektdaten:</strong> Bis zur manuellen Löschung durch den Nutzer</li>
                <li><strong>Log-Dateien:</strong> Maximal 30 Tage</li>
                <li><strong>Backup-Daten:</strong> Maximal 90 Tage</li>
                <li><strong>Rechnungsdaten:</strong> 10 Jahre (§ 147 AO)</li>
              </ul>
            </div>
          </section>

          <!-- Änderungen -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">10. Änderungen dieser Datenschutzerklärung</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Wir behalten uns vor, diese Datenschutzerklärung anzupassen, damit sie stets den aktuellen 
                rechtlichen Anforderungen entspricht oder um Änderungen unserer Leistungen in der 
                Datenschutzerklärung umzusetzen. Für Ihren erneuten Besuch gilt dann die neue Datenschutzerklärung.
              </p>
            </div>
          </section>

          <!-- Kontakt -->
          <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-900 mb-4">11. Fragen zum Datenschutz</h2>
            <div class="prose prose-gray max-w-none">
              <p class="text-gray-700 leading-relaxed">
                Wenn Sie Fragen zum Datenschutz haben, schreiben Sie uns bitte eine E-Mail oder wenden Sie 
                sich direkt an die für den Datenschutz verantwortliche Person in unserer Organisation:
              </p>
              <p class="text-gray-700 leading-relaxed">
                <strong>Datenschutzbeauftragter:</strong><br>
                E-Mail: 
                <a :href="`mailto:${brandingData.dpo_email || 'datenschutz@chiliview.com'}`" 
                   class="text-blue-600 hover:text-blue-800">
                  {{ brandingData.dpo_email || 'datenschutz@chiliview.com' }}
                </a>
              </p>
            </div>
          </section>
        </div>
      </div>

      <!-- Footer Navigation -->
      <div class="mt-12 text-center">
        <div class="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
          <router-link to="/imprint" class="hover:text-gray-900">Impressum</router-link>
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
  name: 'Privacy',
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

.prose ul {
  margin-bottom: 1rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

.prose a {
  text-decoration: underline;
}

.prose a:hover {
  text-decoration: none;
}
</style>