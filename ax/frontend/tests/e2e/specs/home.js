describe('Create form', () => {
  it('Creates new form', () => {
    cy.visit('/admin/home');
    const formName = 'Cypress ax home test7';
    cy.get('[data-cy=create-form-btn]').click();
    cy.get('[data-cy=new-form-name]').type(formName);
    cy.get('[data-cy=new-form-db-name]').type('ax_cypress7');
    cy.get('[data-cy=new-form-btn]').click();
    cy.wait(500);
    cy.get('[data-cy=forms-tree] > ul > li').then($list => {
      const names = [];
      for (let i = 0; i < $list.length; i += 1) {
        names.push($list[i].innerText.trim());
      }
      expect(names).to.include(formName);
    });
  });
});

describe('Folder functionality works', () => {
  it('Creates new folder, deletes folder', () => {
    cy.visit('/admin/home');
    const folderName = 'Cypress folder';
    cy.get('[data-cy=create-folder-btn]').click();
    cy.get('[data-cy=new-folder-name]').type(folderName);
    cy.get('[data-cy=new-folder-btn]').click();
    cy.wait(500);
    const names = [];
    cy.get('[data-cy=forms-tree] > ul > li').each(($el, index, $list) => {
      names.push($el[0].innerText);
    }).then($list => {
      expect(names).to.include(folderName);
      cy.get('[data-cy=forms-tree] > ul > li').contains(folderName).click();
      cy.get('[data-cy=new-folder-delete-btn]').click();
      cy.get('[action-key=true]').click();
      cy.get('[data-cy=forms-tree]').then($tree => {
        cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
          expect($lilist).not.to.contain(folderName);
        }).not.to.contains(folderName);
      });

      // .then($li => {
      //   cy.log($li);
      // });
    });
  });
});
