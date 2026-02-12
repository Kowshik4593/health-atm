'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

export default function LandingPage() {
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Detect system theme
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setTheme(mediaQuery.matches ? 'dark' : 'light');

    const handler = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? 'dark' : 'light');
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const isDark = theme === 'dark';

  const content = {
    en: {
      hero: {
        headline: "Lung CT Scan at Your Village Health Center",
        subheadline: "Get fast, accurate lung health reports in all Indian languages - right in your neighborhood",
        cta1: "For Operators: Upload Scan",
        cta2: "For Doctors: Review Reports",
        cta3: "Learn How It Works"
      },
      howItWorks: {
        title: "How It Works",
        step1: {
          title: "Get Your CT Scan",
          desc: "Visit your local health center"
        },
        step2: {
          title: "AI Checks Your Lungs",
          desc: "Smart computer checks for issues"
        },
        step3: {
          title: "Get Report",
          desc: "Doctor reviews & explains results"
        }
      },
      benefits: {
        title: "Why Choose Us",
        benefit1: {
          title: "Available Locally",
          desc: "No need to travel to big cities - available at your village health center"
        },
        benefit2: {
          title: "Fast Results",
          desc: "Get your report in minutes, not weeks"
        },
        benefit3: {
          title: "Your Language",
          desc: "Reports in all Indian languages - easy to understand"
        },
        benefit4: {
          title: "Doctor Approved",
          desc: "Every report reviewed by a qualified doctor"
        }
      },
      whoIsThisFor: {
        title: "Who Is This For?",
        patients: {
          title: "For Patients",
          desc: "Quick, affordable lung check-ups near your home",
          cta: "Find Nearest Center"
        },
        operators: {
          title: "For Health Workers",
          desc: "Easy-to-use system for CT scan uploads",
          cta: "Operator Login"
        },
        doctors: {
          title: "For Doctors",
          desc: "Review cases from anywhere, help more patients",
          cta: "Doctor Login"
        }
      },
      demo: {
        title: "See What a Report Looks Like",
        toggle1: "Normal View",
        toggle2: "Highlighted",
        sampleReport: "Sample Report Preview:",
        reportText: "No major issues found. Small spot detected - doctor will review and explain."
      },
      trust: {
        title: "Why Trust Us?",
        point1: {
          title: "Works Offline",
          desc: "No internet needed at health center"
        },
        point2: {
          title: "Private & Safe",
          desc: "Your data stays secure"
        },
        point3: {
          title: "Doctor Verified",
          desc: "Real doctors review every case"
        },
        point4: {
          title: "Proven Accurate",
          desc: "Tested by medical experts"
        }
      },
      impact: {
        title: "Our Impact",
        stat1: {
          number: "500+",
          label: "Patients Helped"
        },
        stat2: {
          number: "50+",
          label: "Villages Covered"
        },
        stat3: {
          number: "95%",
          label: "Accurate Results"
        }
      },
      footer: {
        about: "About",
        howItWorks: "How It Works",
        findCenter: "Find Center",
        contact: "Contact",
        privacy: "Privacy",
        operatorLogin: "Operator Login",
        doctorLogin: "Doctor Login",
        language: "Language"
      }
    },
    hi: {
      hero: {
        headline: "अपने गाँव के स्वास्थ्य केंद्र पर फेफड़ों का CT स्कैन",
        subheadline: "सभी भारतीय भाषाओं में तेज़, सटीक फेफड़े स्वास्थ्य रिपोर्ट प्राप्त करें - अपने पड़ोस में",
        cta1: "ऑपरेटर्स के लिए: स्कैन अपलोड करें",
        cta2: "डॉक्टरों के लिए: रिपोर्ट देखें",
        cta3: "यह कैसे काम करता है"
      },
      howItWorks: {
        title: "यह कैसे काम करता है",
        step1: {
          title: "अपना CT स्कैन करवाएं",
          desc: "अपने स्थानीय स्वास्थ्य केंद्र पर जाएं"
        },
        step2: {
          title: "AI आपके फेफड़ों की जांच करता है",
          desc: "स्मार्ट कंप्यूटर समस्याओं की जांच करता है"
        },
        step3: {
          title: "रिपोर्ट प्राप्त करें",
          desc: "डॉक्टर समीक्षा करते हैं और परिणाम समझाते हैं"
        }
      },
      benefits: {
        title: "हमें क्यों चुनें",
        benefit1: {
          title: "स्थानीय रूप से उपलब्ध",
          desc: "बड़े शहरों की यात्रा करने की आवश्यकता नहीं - आपके गाँव के स्वास्थ्य केंद्र पर उपलब्ध"
        },
        benefit2: {
          title: "तेज़ परिणाम",
          desc: "हफ्तों नहीं, मिनटों में अपनी रिपोर्ट प्राप्त करें"
        },
        benefit3: {
          title: "आपकी भाषा",
          desc: "सभी भारतीय भाषाओं में रिपोर्ट - समझने में आसान"
        },
        benefit4: {
          title: "डॉक्टर द्वारा स्वीकृत",
          desc: "हर रिपोर्ट एक योग्य डॉक्टर द्वारा समीक्षित"
        }
      },
      whoIsThisFor: {
        title: "यह किसके लिए है?",
        patients: {
          title: "मरीजों के लिए",
          desc: "अपने घर के पास त्वरित, किफायती फेफड़े की जांच",
          cta: "निकटतम केंद्र खोजें"
        },
        operators: {
          title: "स्वास्थ्य कर्मियों के लिए",
          desc: "CT स्कैन अपलोड के लिए उपयोग में आसान सिस्टम",
          cta: "ऑपरेटर लॉगिन"
        },
        doctors: {
          title: "डॉक्टरों के लिए",
          desc: "कहीं से भी मामलों की समीक्षा करें, अधिक रोगियों की मदद करें",
          cta: "डॉक्टर लॉगिन"
        }
      },
      demo: {
        title: "देखें रिपोर्ट कैसी दिखती है",
        toggle1: "सामान्य दृश्य",
        toggle2: "हाइलाइट किया गया",
        sampleReport: "नमूना रिपोर्ट पूर्वावलोकन:",
        reportText: "कोई बड़ी समस्या नहीं मिली। छोटा धब्बा पाया गया - डॉक्टर समीक्षा करेंगे और समझाएंगे।"
      },
      trust: {
        title: "हम पर भरोसा क्यों करें?",
        point1: {
          title: "ऑफलाइन काम करता है",
          desc: "स्वास्थ्य केंद्र पर इंटरनेट की आवश्यकता नहीं"
        },
        point2: {
          title: "निजी और सुरक्षित",
          desc: "आपका डेटा सुरक्षित रहता है"
        },
        point3: {
          title: "डॉक्टर द्वारा सत्यापित",
          desc: "वास्तविक डॉक्टर हर मामले की समीक्षा करते हैं"
        },
        point4: {
          title: "सिद्ध सटीकता",
          desc: "चिकित्सा विशेषज्ञों द्वारा परीक्षित"
        }
      },
      impact: {
        title: "हमारा प्रभाव",
        stat1: {
          number: "500+",
          label: "मरीजों की मदद की"
        },
        stat2: {
          number: "50+",
          label: "गाँव कवर किए"
        },
        stat3: {
          number: "95%",
          label: "सटीक परिणाम"
        }
      },
      footer: {
        about: "के बारे में",
        howItWorks: "यह कैसे काम करता है",
        findCenter: "केंद्र खोजें",
        contact: "संपर्क करें",
        privacy: "गोपनीयता",
        operatorLogin: "ऑपरेटर लॉगिन",
        doctorLogin: "डॉक्टर लॉगिन",
        language: "भाषा"
      }
    }
  };

  const t = content[language];

  const [demoView, setDemoView] = useState<'normal' | 'highlighted'>('normal');

  return (
    <div className={`min-h-screen transition-colors ${isDark ? 'bg-black' : 'bg-white'}`}>
      {/* Language Toggle - Fixed Top Right */}
      <div className="fixed top-4 right-4 z-50">
        <div className={`flex gap-2 p-1 rounded-lg border ${
          isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200 shadow-sm'
        }`}>
          <button
            onClick={() => setLanguage('en')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              language === 'en'
                ? isDark
                  ? 'bg-white text-black'
                  : 'bg-gray-900 text-white'
                : isDark
                  ? 'text-neutral-400 hover:text-white'
                  : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            English
          </button>
          <button
            onClick={() => setLanguage('hi')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              language === 'hi'
                ? isDark
                  ? 'bg-white text-black'
                  : 'bg-gray-900 text-white'
                : isDark
                  ? 'text-neutral-400 hover:text-white'
                  : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            हिंदी
          </button>
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 py-20 sm:py-32">
          <div className="text-center max-w-4xl mx-auto">
            {/* Logo/Icon */}
            <div className="flex justify-center mb-8">
              <div className={`w-16 h-16 rounded-xl flex items-center justify-center ${
                isDark ? 'bg-neutral-900' : 'bg-gray-100'
              }`}>
                <svg className={`w-9 h-9 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
            </div>

            {/* Headline */}
            <h1 className={`text-4xl sm:text-5xl md:text-6xl font-bold mb-6 ${
              isDark ? 'text-white' : 'text-gray-900'
            }`}>
              {t.hero.headline}
            </h1>

            {/* Subheadline */}
            <p className={`text-lg sm:text-xl mb-12 max-w-3xl mx-auto ${
              isDark ? 'text-neutral-300' : 'text-gray-700'
            }`}>
              {t.hero.subheadline}
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/login"
                className={`w-full sm:w-auto px-8 py-4 rounded-lg font-medium transition-colors ${
                  isDark
                    ? 'bg-white text-black hover:bg-neutral-100'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {t.hero.cta1}
              </Link>
              <Link
                href="/login"
                className={`w-full sm:w-auto px-8 py-4 rounded-lg font-medium transition-colors border ${
                  isDark
                    ? 'border-neutral-700 text-white hover:bg-neutral-900'
                    : 'border-gray-300 text-gray-900 hover:bg-gray-50'
                }`}
              >
                {t.hero.cta2}
              </Link>
              <button
                onClick={() => {
                  document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' });
                }}
                className={`w-full sm:w-auto px-8 py-4 rounded-lg font-medium transition-colors ${
                  isDark
                    ? 'text-neutral-400 hover:text-white'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {t.hero.cta3}
              </button>
            </div>
          </div>

          {/* Hero Visual - Simple Illustration */}
          <div className="mt-20 max-w-5xl mx-auto">
            <div className={`rounded-2xl p-8 border ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-gray-50 border-gray-200'
            }`}>
              <div className="grid md:grid-cols-3 gap-8 text-center">
                {/* Village Health Center */}
                <div className="flex flex-col items-center">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 ${
                    isDark ? 'bg-neutral-800' : 'bg-white'
                  }`}>
                    <svg className={`w-10 h-10 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <p className={`text-sm font-medium ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                    {language === 'en' ? 'Village Health Center' : 'गाँव स्वास्थ्य केंद्र'}
                  </p>
                </div>

                {/* CT Scan */}
                <div className="flex flex-col items-center">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 ${
                    isDark ? 'bg-neutral-800' : 'bg-white'
                  }`}>
                    <svg className={`w-10 h-10 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className={`text-sm font-medium ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                    {language === 'en' ? 'AI Analysis' : 'AI विश्लेषण'}
                  </p>
                </div>

                {/* Report */}
                <div className="flex flex-col items-center">
                  <div className={`w-20 h-20 rounded-full flex items-center justify-center mb-4 ${
                    isDark ? 'bg-neutral-800' : 'bg-white'
                  }`}>
                    <svg className={`w-10 h-10 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className={`text-sm font-medium ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                    {language === 'en' ? 'Report Ready' : 'रिपोर्ट तैयार'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className={`py-20 border-t ${
        isDark ? 'border-neutral-800' : 'border-gray-200'
      }`}>
        <div className="max-w-7xl mx-auto px-4">
          <h2 className={`text-3xl sm:text-4xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {t.howItWorks.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Step 1 */}
            <div className="text-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold ${
                isDark ? 'bg-neutral-900 text-white' : 'bg-gray-900 text-white'
              }`}>
                1
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.howItWorks.step1.title}
              </h3>
              <p className={`${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.howItWorks.step1.desc}
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold ${
                isDark ? 'bg-neutral-900 text-white' : 'bg-gray-900 text-white'
              }`}>
                2
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.howItWorks.step2.title}
              </h3>
              <p className={`${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.howItWorks.step2.desc}
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center">
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 text-2xl font-bold ${
                isDark ? 'bg-neutral-900 text-white' : 'bg-gray-900 text-white'
              }`}>
                3
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.howItWorks.step3.title}
              </h3>
              <p className={`${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.howItWorks.step3.desc}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className={`py-20 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4">
          <h2 className={`text-3xl sm:text-4xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {t.benefits.title}
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Benefit 1 */}
            <div className={`p-6 rounded-xl border ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-6 h-6 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.benefits.benefit1.title}
              </h3>
              <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.benefits.benefit1.desc}
              </p>
            </div>

            {/* Benefit 2 */}
            <div className={`p-6 rounded-xl border ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-6 h-6 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.benefits.benefit2.title}
              </h3>
              <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.benefits.benefit2.desc}
              </p>
            </div>

            {/* Benefit 3 */}
            <div className={`p-6 rounded-xl border ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-6 h-6 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                </svg>
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.benefits.benefit3.title}
              </h3>
              <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.benefits.benefit3.desc}
              </p>
            </div>

            {/* Benefit 4 */}
            <div className={`p-6 rounded-xl border ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-6 h-6 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className={`text-lg font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.benefits.benefit4.title}
              </h3>
              <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.benefits.benefit4.desc}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Who Is This For Section */}
      <section className={`py-20 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4">
          <h2 className={`text-3xl sm:text-4xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {t.whoIsThisFor.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Patients */}
            <div className={`p-8 rounded-xl border text-center ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-8 h-8 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.whoIsThisFor.patients.title}
              </h3>
              <p className={`mb-6 ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.whoIsThisFor.patients.desc}
              </p>
              <button className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                isDark
                  ? 'bg-white text-black hover:bg-neutral-100'
                  : 'bg-gray-900 text-white hover:bg-gray-800'
              }`}>
                {t.whoIsThisFor.patients.cta}
              </button>
            </div>

            {/* Operators */}
            <div className={`p-8 rounded-xl border text-center ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-8 h-8 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.whoIsThisFor.operators.title}
              </h3>
              <p className={`mb-6 ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.whoIsThisFor.operators.desc}
              </p>
              <Link
                href="/login"
                className={`inline-block px-6 py-3 rounded-lg font-medium transition-colors ${
                  isDark
                    ? 'bg-white text-black hover:bg-neutral-100'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {t.whoIsThisFor.operators.cta}
              </Link>
            </div>

            {/* Doctors */}
            <div className={`p-8 rounded-xl border text-center ${
              isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
            }`}>
              <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6 ${
                isDark ? 'bg-neutral-800' : 'bg-gray-100'
              }`}>
                <svg className={`w-8 h-8 ${isDark ? 'text-white' : 'text-gray-900'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <h3 className={`text-xl font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.whoIsThisFor.doctors.title}
              </h3>
              <p className={`mb-6 ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.whoIsThisFor.doctors.desc}
              </p>
              <Link
                href="/login"
                className={`inline-block px-6 py-3 rounded-lg font-medium transition-colors ${
                  isDark
                    ? 'bg-white text-black hover:bg-neutral-100'
                    : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
              >
                {t.whoIsThisFor.doctors.cta}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className={`py-20 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
        <div className="max-w-5xl mx-auto px-4">
          <h2 className={`text-3xl sm:text-4xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {t.demo.title}
          </h2>

          <div className={`rounded-2xl border overflow-hidden ${
            isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
          }`}>
            {/* Toggle */}
            <div className={`p-4 border-b flex justify-center gap-4 ${
              isDark ? 'border-neutral-800' : 'border-gray-200'
            }`}>
              <button
                onClick={() => setDemoView('normal')}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  demoView === 'normal'
                    ? isDark
                      ? 'bg-white text-black'
                      : 'bg-gray-900 text-white'
                    : isDark
                      ? 'text-neutral-400 hover:text-white'
                      : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {t.demo.toggle1}
              </button>
              <button
                onClick={() => setDemoView('highlighted')}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  demoView === 'highlighted'
                    ? isDark
                      ? 'bg-white text-black'
                      : 'bg-gray-900 text-white'
                    : isDark
                      ? 'text-neutral-400 hover:text-white'
                      : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {t.demo.toggle2}
              </button>
            </div>

            {/* Image Preview */}
            <div className={`p-8 ${isDark ? 'bg-neutral-950' : 'bg-gray-50'}`}>
              <div className={`aspect-video rounded-lg flex items-center justify-center ${
                isDark ? 'bg-neutral-900' : 'bg-white'
              }`}>
                {demoView === 'normal' ? (
                  <div className="text-center p-8">
                    <svg className={`w-24 h-24 mx-auto mb-4 ${isDark ? 'text-neutral-700' : 'text-gray-300'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <p className={`${isDark ? 'text-neutral-400' : 'text-gray-500'}`}>
                      {language === 'en' ? 'Normal CT Scan View' : 'सामान्य CT स्कैन दृश्य'}
                    </p>
                  </div>
                ) : (
                  <div className="text-center p-8">
                    <svg className={`w-24 h-24 mx-auto mb-4 ${isDark ? 'text-neutral-700' : 'text-gray-300'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className={`${isDark ? 'text-neutral-400' : 'text-gray-500'}`}>
                      {language === 'en' ? 'Highlighted Areas of Interest' : 'रुचि के हाइलाइट किए गए क्षेत्र'}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Sample Report */}
            <div className={`p-6 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
              <h3 className={`font-semibold mb-3 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                {t.demo.sampleReport}
              </h3>
              <p className={`${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                {t.demo.reportText}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className={`py-20 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4">
          <h2 className={`text-3xl sm:text-4xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {t.trust.title}
          </h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[t.trust.point1, t.trust.point2, t.trust.point3, t.trust.point4].map((point, idx) => (
              <div key={idx} className="text-center">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 ${
                  isDark ? 'bg-green-950' : 'bg-green-100'
                }`}>
                  <svg className={`w-6 h-6 ${isDark ? 'text-green-400' : 'text-green-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h3 className={`font-semibold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {point.title}
                </h3>
                <p className={`text-sm ${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                  {point.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className={`py-20 border-t ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4">
          <h2 className={`text-3xl sm:text-4xl font-bold text-center mb-16 ${
            isDark ? 'text-white' : 'text-gray-900'
          }`}>
            {t.impact.title}
          </h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[t.impact.stat1, t.impact.stat2, t.impact.stat3].map((stat, idx) => (
              <div key={idx} className={`p-8 rounded-xl border text-center ${
                isDark ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-200'
              }`}>
                <div className={`text-5xl font-bold mb-2 ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {stat.number}
                </div>
                <div className={`${isDark ? 'text-neutral-400' : 'text-gray-600'}`}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`border-t py-12 ${isDark ? 'border-neutral-800' : 'border-gray-200'}`}>
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 mb-8">
            {/* Links */}
            <div className="flex flex-wrap gap-6">
              <a href="#" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.about}
              </a>
              <a href="#how-it-works" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.howItWorks}
              </a>
              <a href="#" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.findCenter}
              </a>
              <a href="#" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.contact}
              </a>
              <a href="#" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.privacy}
              </a>
            </div>

            {/* Auth Links */}
            <div className="flex flex-wrap gap-6 md:justify-end">
              <Link href="/login" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.operatorLogin}
              </Link>
              <Link href="/login" className={`text-sm hover:underline ${isDark ? 'text-neutral-400 hover:text-white' : 'text-gray-600 hover:text-gray-900'}`}>
                {t.footer.doctorLogin}
              </Link>
            </div>
          </div>

          {/* Copyright */}
          <div className={`text-center text-sm pt-8 border-t ${
            isDark ? 'border-neutral-800 text-neutral-400' : 'border-gray-200 text-gray-600'
          }`}>
            © {new Date().getFullYear()} AI Lung Health. All rights reserved.
          </div>
        </div>
      </footer>

      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap');
        
        * {
          font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        html {
          scroll-behavior: smooth;
        }
      `}</style>
    </div>
  );
}