
// ☐ Update folder
// ✔ Create form @done(19-03-23 23:47)
// ☐ Drag form to folder
// ☐ Go to form constructor
// ☐ Update form name and dbName
// ☐ Check url changed, name in toolbar changed
// ☐ Delete form
// ☐ Delete folder

// describe('Create form', () => {
//   it('Creates new form', () => {
//     cy.visit('/admin/home');
//     const formName = 'Cypress ax home test7';
//     cy.get('[data-cy=create-form-btn]').click();
//     cy.get('[data-cy=new-form-name]').type(formName);
//     cy.get('[data-cy=new-form-db-name]').type('ax_cypress7');
//     cy.get('[data-cy=new-form-btn]').click();
//     cy.wait(500);
//     cy.get('[data-cy=forms-tree] > ul > li').then($list => {
//       const names = [];
//       for (let i = 0; i < $list.length; i += 1) {
//         names.push($list[i].innerText.trim());
//       }
//       expect(names).to.include(formName);
//     });
//   });

// });

describe('Home functions work. CRUD for folder and forms', () => {
  context('home', () => {
    const folderName = 'Cypress folder';
    const formName = 'Cypress ax home test';
    const formDbName = 'ax_cypress_test';

    // it('Creates new folder', () => {
    //   cy.visit('/admin/home');
    //   cy.get('[data-cy=create-folder-btn]').click();
    //   cy.get('[data-cy=new-folder-name]').type(folderName);
    //   cy.get('[data-cy=new-folder-btn]').click();
    //   cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
    //     expect($lilist).to.contain(folderName);
    //   });
    // });

    // it('Updates folder name', () => {
    //   cy.wait(10);
    //   cy.get('[data-cy=forms-tree] > ul > li').contains(folderName).click();
    //   cy.get('[data-cy=new-folder-name]').type(' cy_edited');
    //   cy.get('[data-cy=new-folder-btn]').click();
    //   cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
    //     expect($lilist).to.contain(`${folderName} cy_edited`);
    //   });
    // });

    // it('Deletes folder', () => {
    //   cy.wait(10);
    //   cy.get('[data-cy=forms-tree] > ul > li').contains(folderName).click();
    //   cy.get('[data-cy=new-folder-delete-btn]').click();
    //   cy.get('[action-key="true"]').click();
    //   cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
    //     expect($lilist).not.to.contain(`${folderName} cy_edited`);
    //   });
    // });

    it('Creates form', () => {
      cy.visit('/admin/home');
      cy.get('[data-cy=create-form-btn]').click();
      cy.get('[data-cy=new-form-name]').type(formName);
      cy.get('[data-cy=new-form-db-name]').type(formDbName);
      cy.get('[data-cy=new-form-btn]').click().then(() => {
        cy.wait(100);
        cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
          expect($lilist).not.to.contain(`${formName}`);
        });
      });
    });

    it('Updates form name and dbName', () => {
      cy.wait(100);
      cy.visit(`/admin/${formDbName}/form`);
      cy.get('[data-cy=current-form-breadcrumb] > button').click();
      cy.get('[data-cy=new-form-name]').type(' #findme');
      cy.get('[data-cy=new-form-db-name]').type('_test');
      cy.get('[data-cy=update-form-btn]').click().then(() => {
        cy.wait(100);
        cy.url().should('include', `${formDbName}_test`);
        cy.get('[data-cy=current-form-breadcrumb]').should($span => {
          expect($span).to.contain(`${formName} #findme`);
        });
      });
    });

    it('Deletes form', () => {
      cy.wait(100);
      cy.get('[data-cy=current-form-breadcrumb] > button').click();
      cy.get('[data-cy=delete-form-btn]').click();
      cy.get('[action-key="true"]').click().then(() => {
        cy.wait(10);
        cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
          expect($lilist).not.to.contain(`${formName} #findme`);
        });
      });
    });
    //
  });
});


// it('Deletes folder') {
//     const names = [];
//     cy.get('[data-cy=forms-tree] > ul > li').each(($el, index, $list) => {
//       names.push($el[0].innerText);
//     }).then($list => {
//       expect(names).to.include(folderName);
//       cy.get('[data-cy=forms-tree] > ul > li').contains(folderName).click();
//       cy.get('[data-cy=new-folder-delete-btn]').click();
//       cy.get('[action-key=true]').click();
//       cy.get('[data-cy=forms-tree]').then($tree => {
//         cy.get('[data-cy=forms-tree] > ul > li').should($lilist => {
//           expect($lilist).not.to.contain(folderName);
//         }).not.to.contains(folderName);
//       });
//     });
//   });
// });
