module.exports = {
  testEnvironment: 'jsdom',
  roots: ['../tests'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
};
