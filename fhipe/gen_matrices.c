/**
 * Copyright (c) 2016, Kevin Lewi
 * 
 * Permission to use, copy, modify, and/or distribute this software for any
 * purpose with or without fee is hereby granted, provided that the above
 * copyright notice and this permission notice appear in all copies.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
 * REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
 * INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
 * LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
 * OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
 * PERFORMANCE OF THIS SOFTWARE.
 */

#include "gen_matrices.h"

/**
 * Main function
 *
 * Must be called with the parameters n, p, and a seed, separated by spaces
 *
 */
int main(int argc, char *argv[]) {
  print_random_matrices_with_adj(argv[1], argv[2], argv[3], argv[4]);
  return 0;
}

void fmpz_mat_mul_modp(fmpz_mat_t a, fmpz_mat_t b, fmpz_mat_t c, int n,
    fmpz_t p) {
  fmpz_mat_mul(a, b, c);
  for(int i = 0; i < n; i++) {
    for(int j = 0; j < n; j++) {
      fmpz_mod(fmpz_mat_entry(a, i, j), fmpz_mat_entry(a, i, j), p);
    }
  }
}

void print_random_matrices_with_adj(char *n_str, char *p_str, char *simulated,
    char *seed) {
  int n = atoi(n_str);
  int is_simulated_setup = atoi(simulated);
  cryptorand_t randstate;
  cryptorand_initseed(randstate, seed ? seed : "", NULL);
  fmpz_t modp;
  fmpz_init(modp);
  fmpz_set_str(modp, p_str, 10);

  fmpz_mat_t a;
  fmpz_mat_init(a, n, n);
 
  for(int i = 0; i < n; i++) {
    for(int j = 0; j < n; j++) {
      fmpz_randm_crypto(fmpz_mat_entry(a, i, j), randstate, modp);
    }
  }

  fmpz_t det;
  fmpz_init(det);

  fmpz_mat_t adjugate;
  fmpz_mat_init(adjugate, n, n);

  fmpz_mat_t prod;
  fmpz_mat_init(prod, n, n);

  fmpz_mat_t check;
  fmpz_mat_init(check, n, n);

  if(is_simulated_setup) {
    /* set det and adj randomly */
    fmpz_randm_crypto(det, randstate, modp);

    for(int i = 0; i < n; i++) {
      for(int j = 0; j < n; j++) {
        fmpz_randm_crypto(fmpz_mat_entry(adjugate, i, j), randstate, modp);
      }
    }
  } else {
    fmpz_modp_matrix_det(det, a, n, modp);
    if (fmpz_is_zero(det)) {
      fprintf(stderr, "ERROR: Random matrix was not invertible.\n");
      goto exit_det;
    }

    fmpz_modp_matrix_adjugate(adjugate, a, n, modp);
    fmpz_mat_transpose(adjugate, adjugate);

        fmpz_mat_mul_modp(prod, a, adjugate, n, modp);

    /* check that the adjugate and determinant were computed correctly */
    fmpz_mat_one(check);
    fmpz_mat_scalar_mul_fmpz(check, check, det);

    int status = fmpz_mat_equal(prod, check);
    if (status == 0) {
      fprintf(stderr, "ERROR: Failed to produce the proper matrices.\n");
      goto exit;
    }
  }

  /* print the resulting values */
  fmpz_fprint(stdout, det);
  printf("\n");
  fmpz_mat_fprint(stdout, a);
  printf("\n");
  fmpz_mat_transpose(adjugate, adjugate);
  fmpz_mat_fprint(stdout, adjugate);
  printf("\n");

exit:
  fmpz_mat_clear(a);
  fmpz_mat_clear(prod);
  fmpz_mat_clear(check);

exit_det:
  fmpz_mat_clear(adjugate);
  fmpz_clear(det);

  cryptorand_clear(randstate);
}

void fmpz_modp_matrix_det(fmpz_t det, fmpz_mat_t a, int n, fmpz_t p) {
  assert(n >= 1);

  if(n == 1) {
    fmpz_set(det, fmpz_mat_entry(a, 0, 0));
    return;
  }
	
  if (n == 2) {
    fmpz_t tmp1;
    fmpz_init(tmp1);
    fmpz_mul(tmp1, fmpz_mat_entry(a,0,0), fmpz_mat_entry(a,1,1));
    fmpz_mod(tmp1, tmp1, p);
    fmpz_t tmp2;
    fmpz_init(tmp2);
    fmpz_mul(tmp2, fmpz_mat_entry(a,1,0), fmpz_mat_entry(a,0,1));
    fmpz_mod(tmp2, tmp2, p);
    fmpz_sub(det, tmp1, tmp2);
    fmpz_mod(det, det, p);
    fmpz_clear(tmp1);
    fmpz_clear(tmp2);
    return;
  }

  fmpz_mat_t m;
  fmpz_mat_init_set(m, a);

  fmpz_t tmp;
  fmpz_init(tmp);
  fmpz_t multfactor;
  fmpz_init(multfactor);

  int num_swaps = 0;

  for(int j = 0; j < n; j++) {
    for(int i = j+1; i < n; i++) {

      if(fmpz_is_zero(fmpz_mat_entry(m, j, j))) {
        // find first row that isn't a zero, and swap
        int h;
        for(h = j+1; h < n; h++) {
          if(!fmpz_is_zero(fmpz_mat_entry(m, h, j))) {
            // found the row
            break;
          }
        }

        if(h == n) {
          // matrix is not invertible
          fmpz_set_ui(det, 0);
          fmpz_clear(multfactor);
          fmpz_clear(tmp);
          fmpz_mat_clear(m);
          return;
        }

        // swap row h with row j
        for(int k = 0; k < n; k++) {
          fmpz_set(tmp, fmpz_mat_entry(m, h, k));
          fmpz_set(fmpz_mat_entry(m, h, k), fmpz_mat_entry(m, j, k));
          fmpz_set(fmpz_mat_entry(m, j, k), tmp);
        }

        num_swaps++;
      }

      fmpz_invmod(multfactor, fmpz_mat_entry(m, j, j), p);
      fmpz_mul(multfactor, multfactor, fmpz_mat_entry(m, i, j));
      fmpz_mod(multfactor, multfactor, p);

#pragma omp parallel for
      for(int k = j; k < n; k++) {
        fmpz_t tmp2;
        fmpz_init(tmp2);
        fmpz_mul(tmp2, fmpz_mat_entry(m, j, k), multfactor);
        fmpz_sub(fmpz_mat_entry(m, i, k), fmpz_mat_entry(m, i, k), tmp2);
        fmpz_mod(fmpz_mat_entry(m, i, k), fmpz_mat_entry(m, i, k), p);
        fmpz_clear(tmp2);
      }
    }
  }

  fmpz_clear(multfactor);
  fmpz_clear(tmp);

  fmpz_set_ui(det, 1);

  for(int j = 0; j < n; j++) {
    fmpz_mul(det, det, fmpz_mat_entry(m, j, j));
  }
  if(num_swaps % 2 == 1) {
    fmpz_neg(det, det);
  }
  fmpz_mod(det, det, p);
  fmpz_mat_clear(m);
}

void fmpz_modp_matrix_adjugate(fmpz_mat_t b, fmpz_mat_t a, int n, fmpz_t p) {
  if(n == 1) {
    fmpz_set_ui(fmpz_mat_entry(b, 0, 0), 1);
    return;
  }

  fmpz_t det;
  fmpz_init(det);

  fmpz_mat_t c;
  fmpz_mat_init(c, n-1, n-1);

  for (int j = 0; j < n; j++) {
    for (int i = 0; i < n; i++) {
      /* Form the adjoint a_ij */
      for (int i_iter = 0, i1 = 0; i_iter < n; i_iter++, i1++) {
        if (i_iter == i) {
          i1--;
          continue;
        }
        for (int j_iter = 0, j1 = 0; j_iter < n; j_iter++, j1++) {
          if (j_iter == j) {
            j1--;
            continue;
          }
          fmpz_set(fmpz_mat_entry(c, i1, j1), fmpz_mat_entry(a, i_iter, j_iter));
        }
      }
			
      /* Calculate the determinant */
      fmpz_modp_matrix_det(det, c, n-1, p);

      /* Fill in the elements of the adjugate */
      if((i+j) % 2 == 1) {
        fmpz_negmod(det, det, p);
      }
      fmpz_mod(det, det, p);
      fmpz_set(fmpz_mat_entry(b, i, j), det);
    }
  }

  fmpz_clear(det);
  fmpz_mat_clear(c);
}
