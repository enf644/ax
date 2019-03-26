// https://docs.cypress.io/api/introduction/api.html

describe('My First Test', () => {
  it('Visits the app root url', () => {
    cy.visit('/admin/home');
    cy.get('[data-cy=user-list] > li').then($list => {
      const len = $list.size();
      cy.log(`before list = ${len}`);
      cy.get('[data-cy=add-new-user]').click();
      cy.log(`after list = ${len}`);
      cy.get('[data-cy=user-list] > li').should('have.length', len + 1);
    });
  });
});
