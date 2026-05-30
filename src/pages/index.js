import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import Translate, {translate} from '@docusaurus/Translate';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx(styles.heroBanner)}>
      {/* 背景光暈(液態玻璃風格) */}
      <div className={styles.halo} aria-hidden="true" />
      <div className="container">
        <div className={styles.heroInner}>
          <p className={styles.heroEyebrow}>
            <Translate id="homepage.hero.eyebrow">Hi, 我是</Translate>
          </p>
          <Heading as="h1" className={styles.heroTitle}>
            {siteConfig.title}
          </Heading>
          <p className={styles.heroSubtitle}>
            <Translate id="homepage.hero.subtitle">
              軟體工程師 · 打造好用的產品與工具
            </Translate>
          </p>
          <p className={styles.heroDescription}>
            <Translate id="homepage.hero.description">
              歡迎來到我的個人網站。這裡記錄了我的經歷、作品,以及一些技術心得。
            </Translate>
          </p>
          <div className={styles.buttons}>
            <Link className="button button--primary button--lg" to="/about">
              <Translate id="homepage.hero.aboutButton">認識我 →</Translate>
            </Link>
            <Link
              className="button button--secondary button--lg"
              to="/projects">
              <Translate id="homepage.hero.projectsButton">
                看我的作品
              </Translate>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={translate({
        id: 'homepage.meta.title',
        message: '首頁',
      })}
      description={translate({
        id: 'homepage.meta.description',
        message: 'Chia-Che 的個人網站 — 自我介紹、作品集與技術部落格。',
      })}>
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
