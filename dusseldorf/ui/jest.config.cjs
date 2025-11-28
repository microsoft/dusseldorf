module.exports = {
  testEnvironment: 'node',
  transform: {
    '^.+\\.(ts|tsx|js|jsx)$': 'babel-jest'
  },
  moduleFileExtensions: ['ts','tsx','js','jsx','json'],
  roots: ['<rootDir>/src'],
  testPathIgnorePatterns: ['/node_modules/','/dist/'],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx,js,jsx}',
    '!src/**/*.d.ts'
  ]
};
