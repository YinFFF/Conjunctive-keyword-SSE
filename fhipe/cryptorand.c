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

#include "cryptorand.h"

void cryptorand_init(cryptorand_t state) {
  cryptorand_initseed(state, DEFAULT_SEED, NULL);
}

void cryptorand_initseed(cryptorand_t state, char *seed, char *additional) {
  state->cryptorand_init = 1;
  state->ctr = 0;
  if(!(state->iv = malloc(EVP_CIPHER_iv_length(AES_ALGORITHM)))) {
    perror("Error setting IV for state");
    return;
  }
  memset(state->iv, 0, EVP_CIPHER_iv_length(AES_ALGORITHM));

  if(additional == NULL) {
    additional = "";
  }

  char *digest;
  if(!(digest = malloc(strlen(seed) + strlen(additional) + 1))) {
    perror("Error setting SHA digest");
    return;
  }

  digest[0] = 0;
  strcat(digest, seed);
  strcat(digest, additional);

  SHA256_CTX sha256;
  if(!SHA256_Init(&sha256)) {
    perror("Error in calling SHA256_Init");
    goto exit_digest;
  }
  
  if(!SHA256_Update(&sha256, digest, strlen(digest))) {
    perror("Error in calling SHA256_Update");
    goto exit_digest;
  }

  if(!SHA256_Final(state->key, &sha256)) {
    perror("Error in calling SHA256_Final");
    goto exit_digest;
  }

exit_digest:
  free(digest);
}

void cryptorand_clear(cryptorand_t state) {
  free(state->iv);
}

void fmpz_randm_crypto(fmpz_t f, cryptorand_t state, const fmpz_t m) {
  mpz_t x, rop;
  mpz_init(x);
  mpz_init(rop);
  fmpz_get_mpz(x, m);
  mpz_urandomm_crypto(rop, state, x);
  fmpz_set_mpz(f, rop);
  mpz_clear(x);
  mpz_clear(rop);
}

void mpz_urandomm_crypto(mpz_t rop, cryptorand_t state, const mpz_t m) {
  unsigned long size = mpz_sizeinbase(m, 2);

  while(1) {
    mpz_urandomb_crypto(rop, state, size);
    if(mpz_cmp(rop, m) < 0) {
      break;
    }
  }
}

void mpz_urandomb_crypto(mpz_t rop, cryptorand_t state, mp_bitcnt_t n) {
  unsigned long ctr_iv;
  #pragma omp critical(update_iv_counter)
  {
    // update the internal counter, works at most 2^64 times
    ctr_iv = state->ctr++;
  }

  memcpy(state->iv, &ctr_iv, sizeof(ctr_iv)); 
  mp_bitcnt_t nb = n/8+1; // number of bytes

  if(!(state->ctx = EVP_CIPHER_CTX_new())) {
    perror("Error in initializing new cipher context");
    return;
  }
  if(!EVP_EncryptInit_ex(state->ctx, AES_ALGORITHM, NULL, state->key,
        state->iv)) {
    perror("Error in calling EncryptInit");
    return;
  }

  unsigned char *output;
  if(!(output = malloc(2 * (nb + EVP_MAX_IV_LENGTH)))) {
    perror("Error in initializing output buffer");
    return;
  }
  mp_bitcnt_t outlen = 0;

  int in_size = nb;
  unsigned char in[in_size];
  memset(in, 0, in_size);

  while(outlen < nb) {
    int buflen = 0;
    if(!EVP_EncryptUpdate(state->ctx, output+outlen, &buflen, in, in_size)) {
      perror("Error in calling EncryptUpdate");
      goto output_exit;
    }
    outlen += buflen;
  }
  int final_len = 0;
  if(!EVP_EncryptFinal(state->ctx, output+outlen, &final_len)) {
    perror("Error in calling EncryptFinal");
    goto output_exit;
  }
  outlen += final_len;

  if(outlen > nb) {
    outlen = nb; // we will only use nb bytes
  }

  mp_bitcnt_t true_len = outlen + 4;
  mp_bitcnt_t bytelen = outlen;

  unsigned char *buf;
  if(!(buf = malloc(true_len))) {
    perror("Error in initializing buf");
    goto output_exit;
  }
  memset(buf, 0, true_len);
  memcpy(buf+4, output, outlen);
  buf[4] >>= ((outlen*8) - (unsigned int) n);

  for(int i = 3; i >= 0; i--) {
    buf[i] = (unsigned char) (bytelen % (1 << 8));
    bytelen /= (1 << 8);
  }

  // generate a random n-bit number
  FILE *fp;
  if(!(fp = fmemopen(buf, true_len, "rb"))) {
    perror("Error in calling fmemopen");
    goto buf_exit;
  }

  if(!mpz_inp_raw(rop, fp)) {
    fprintf(stderr, "Error in parsing randomness.\n");
  }

  fclose(fp); 

buf_exit:
  free(buf); 

output_exit:
  free(output);

  EVP_CIPHER_CTX_cleanup(state->ctx);
  free(state->ctx);

}

