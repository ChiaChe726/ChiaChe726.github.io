// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Chia-Che",
  tagline: '軟體工程師 · 打造好用的產品與工具',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    // Keep v4 compatibility flags on, but expand the `v4: true` shortcut so we
    // can opt out of two sub-flags that would otherwise break this site as of
    // Docusaurus 3.10:
    //   - fasterByDefault: requires installing the extra `@docusaurus/faster`
    //     package (Rspack/SWC native deps), which we don't want here.
    //   - mdx1CompatDisabledByDefault: tightens MDX parsing and rejects the
    //     `<!-- truncate -->` HTML comments used by the default blog posts.
    v4: {
      removeLegacyPostBuildHeadAttribute: true,
      useCssCascadeLayers: true,
      siteStorageNamespacing: true,
      fasterByDefault: false,
      mdx1CompatDisabledByDefault: false,
    },
  },

  // Set the production url of your site here
  url: 'https://ChiaChe726.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'ChiaChe726',
  projectName: 'ChiaChe726.github.io',
  deploymentBranch: 'gh-pages',

  onBrokenLinks: 'throw',

  // 載入網頁字體:Inter(拉丁)+ Noto Sans TC(中文)
  stylesheets: [
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;700&display=swap',
  ],

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'zh-tw',
    locales: ['zh-tw', 'en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // 把文件區當作「筆記」,網址改成 /notes
          routeBasePath: 'notes',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Chia-Che',
        logo: {
          alt: 'Logo',
          src: 'img/logo.svg',
        },
        items: [
          {to: '/about', label: '關於我', position: 'left'},
          {to: '/projects', label: '作品集', position: 'left'},
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: '筆記',
          },
          {to: '/blog', label: '部落格', position: 'left'},
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            href: 'https://github.com/ChiaChe726',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: '網站',
            items: [
              {label: '關於我', to: '/about'},
              {label: '作品集', to: '/projects'},
              {label: '筆記', to: '/notes/intro'},
              {label: '部落格', to: '/blog'},
            ],
          },
          {
            title: '聯絡 / 社群',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/ChiaChe726',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Chia-Che. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
