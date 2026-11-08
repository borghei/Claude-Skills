import type { StorybookConfig } from '@storybook/nextjs-vite';

const config: StorybookConfig = {
  stories: ['../components/**/*.stories.@(ts|tsx)', '../app/**/*.stories.@(ts|tsx)'],
  framework: { name: '@storybook/nextjs-vite', options: {} },
  staticDirs: ['../public'],
};

export default config;
